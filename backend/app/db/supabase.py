# from supabase import create_client
# import os
# from config import SUPABASE_URL, SUPABASE_KEY

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # Пример: выбрать все записи из существующей таблицы "scripts"
# response = supabase.table("scripts").select("*").execute()
# print(response.data)

# # Пример: вставить новую запись
# new_record = {"title": "Новый сценарий", "text": "Текст"}
# supabase.table("scripts").insert(new_record).execute()
