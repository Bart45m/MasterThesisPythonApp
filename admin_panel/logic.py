import io
from datetime import datetime
from django.db.models import Count, Sum
from accounts.models import Users
from products.models import Product
from orders.models import Order
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class AdminService:

    @staticmethod
    def get_all_users():
        return Users.objects.all().values('id', 'email', 'role')

    @staticmethod
    def update_user_role(user_id, new_role):
        try:
            user = Users.objects.get(id=user_id)
            user.role = new_role
            user.save()
            return True
        except Users.DoesNotExist:
            return False

    @staticmethod
    def get_dashboard_stats():
        total_users = Users.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        
        revenue_agg = Order.objects.aggregate(total=Sum('total_price'))
        total_revenue = revenue_agg['total'] or 0

        status_map = {
            0: 'Pending',
            1: 'Processing',
            2: 'Shipped',
            3: 'Delivered',
            4: 'Cancelled'
        }

        orders_raw = Order.objects.values('status').annotate(count=Count('id'))
        orders_by_status = {}
        for item in orders_raw:
            st_key = status_map.get(item['status'], str(item['status']))
            orders_by_status[st_key] = item['count']

        return {
            'totalUsers': total_users,
            'totalProducts': total_products,
            'totalOrders': total_orders,
            'totalRevenue': total_revenue,
            'ordersByStatus': orders_by_status
        }

    @staticmethod
    def generate_pdf_report():
        stats = AdminService.get_dashboard_stats()
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2b6cb0'),
            spaceAfter=12
        )

        elements.append(Paragraph("Raport Podsumowujący - Panel Administracyjny", title_style))
        elements.append(Paragraph(f"Data wygenerowania: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("<b>Podsumowanie systemu:</b>", styles['Heading2']))
        elements.append(Paragraph(f"- Liczba użytkowników: {stats['totalUsers']}", styles['Normal']))
        elements.append(Paragraph(f"- Liczba produktów: {stats['totalProducts']}", styles['Normal']))
        elements.append(Paragraph(f"- Liczba zamówień: {stats['totalOrders']}", styles['Normal']))
        elements.append(Paragraph(f"- Całkowity przychód: {stats['totalRevenue']:.2f} PLN", styles['Normal']))
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("<b>Zamówienia według statusu:</b>", styles['Heading2']))
        for k, v in stats['ordersByStatus'].items():
            elements.append(Paragraph(f"&nbsp;&nbsp;• {k}: {v}", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()