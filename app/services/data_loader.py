import json
import os
from flask import current_app


class DataLoader:
    @staticmethod
    def _load_file(filename):
        """Βοηθητική μέθοδος για φόρτωση JSON αρχείου"""
        try:
            # Το current_app.root_path μας δίνει τον φάκελο 'app'
            file_path = os.path.join(current_app.root_path, 'data', filename)

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Το αρχείο {filename} δεν βρέθηκε στο {file_path}")
            return []
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return []

    @staticmethod
    def get_payment_methods():
        """Τρόποι Πληρωμής"""
        return DataLoader._load_file('paymentMethods.json')

    @staticmethod
    def get_vat_categories():
        """Κατηγορίες ΦΠΑ"""
        return DataLoader._load_file('vatCategories.json')

    @staticmethod
    def get_quantity_types():
        """Μονάδες Μέτρησης (Τεμάχια, Κιλά, κλπ)"""
        return DataLoader._load_file('quantityTypes.json')

    @staticmethod
    def get_income_classification_types():
        """Τύποι Χαρακτηρισμού Εσόδων (E3_...)"""
        return DataLoader._load_file('classificationTypesIncome.json')

    @staticmethod
    def get_income_classification_categories():
        """Κατηγορίες Χαρακτηρισμού (category1_1...)"""
        return DataLoader._load_file('classificationCategories.json')