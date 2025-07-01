# Generated manually to create missing tables
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('salon', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS "salon_admin" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "telegram_id" bigint NOT NULL UNIQUE,
                "name" varchar(100) NOT NULL,
                "is_active" boolean NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS "salon_feedback" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "client_telegram_id" bigint NOT NULL,
                "client_name" varchar(255) NOT NULL,
                "telegram_username" varchar(255),
                "text" text NOT NULL,
                "created_at" timestamp with time zone NOT NULL,
                "is_processed" boolean NOT NULL,
                "master_id" bigint REFERENCES "salon_master" ("id") ON DELETE SET NULL
            );
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS "salon_admin";
            DROP TABLE IF EXISTS "salon_feedback";
            """
        ),
    ]