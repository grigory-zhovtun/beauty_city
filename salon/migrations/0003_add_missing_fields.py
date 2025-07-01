# Generated manually to add missing fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salon', '0002_create_missing_tables'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Добавляем недостающие поля в таблицу salon_client
            DO $$ 
            BEGIN
                -- consent_given
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name='salon_client' AND column_name='consent_given') THEN
                    ALTER TABLE salon_client ADD COLUMN consent_given boolean DEFAULT false NOT NULL;
                END IF;
                
                -- telegram_username
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name='salon_client' AND column_name='telegram_username') THEN
                    ALTER TABLE salon_client ADD COLUMN telegram_username varchar(255);
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE salon_client DROP COLUMN IF EXISTS consent_given;
            ALTER TABLE salon_client DROP COLUMN IF EXISTS telegram_username;
            """
        ),
    ]