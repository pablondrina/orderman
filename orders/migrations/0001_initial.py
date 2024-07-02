# Generated by Django 5.0.1 on 2024-07-01 13:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscriber_id', models.CharField(max_length=100, unique=True, verbose_name='ID do Assinante')),
                ('order_details', models.TextField(verbose_name='Detalhes do Pedido')),
                ('status', models.CharField(choices=[('placed', 'Novo pedido'), ('confirmed', 'Confirmado'), ('ready_to_pickup', 'Pronto para retirada'), ('concluded', 'Concluído'), ('cancelled', 'Cancelado')], default='placed', max_length=20, verbose_name='Status')),
                ('priority', models.IntegerField(choices=[(1, 'Baixa'), (2, 'Normal'), (3, 'Alta'), (4, 'Urgente')], default=2, verbose_name='Prioridade')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
                'ordering': ['-priority', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Conteúdo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='orders.order', verbose_name='Pedido')),
            ],
            options={
                'verbose_name': 'Comentário',
                'verbose_name_plural': 'Comentários',
                'ordering': ['-created_at'],
            },
        ),
    ]
