import os
import csv


class PriceMachine:

    def __init__(self):
        self.data = []
        self.result = []
        self.name_length = 0

    def load_prices(self, folder_path='.'):
        """
        Сканирует указанный каталог. Ищет файлы со словом 'price' в названии.
        В каждом файле ищет столбцы с названием товара, ценой и весом.
        """
        files = [f for f in os.listdir(folder_path) if 'price' in f.lower()]

        # Обрабатываем каждый файл
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=',')
                    headers = next(reader)

                    # Определяем индексы нужных столбцов
                    product_idx = self._get_column_index(headers, ['название', 'продукт', 'товар', 'наименование'])
                    price_idx = self._get_column_index(headers, ['цена', 'розница'])
                    weight_idx = self._get_column_index(headers, ['фасовка', 'масса', 'вес'])

                    # Считываем строки с нужными данными
                    for row in reader:
                        try:
                            product_name = row[product_idx]
                            price = float(row[price_idx])
                            weight = float(row[weight_idx])
                            price_per_kg = price / weight
                            self.data.append({
                                'name': product_name,
                                'price': price,
                                'weight': weight,
                                'file': file_name,
                                'price_per_kg': price_per_kg
                            })
                        except (ValueError, IndexError):
                            continue  # Игнорируем строки с ошибками в данных
            except ValueError as e:
                print(f"Файл '{file_name}' пропущен: {e}")
            except Exception as e:
                print(f"Ошибка при обработке файла '{file_name}': {e}")

    def _get_column_index(self, headers, possible_names):
        """
        Находит индекс столбца по возможным названиям, игнорируя пробелы.
        """
        headers = [header.strip().lower() for header in headers]
        for idx, header in enumerate(headers):
            if header in possible_names:
                return idx
        raise ValueError("Не найден подходящий столбец")

    def export_to_html(self, fname='output.html'):
        """
        Экспортирует данные в HTML-файл.
        """
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
            <style>
                table, th, td { border: 1px solid black; border-collapse: collapse; }
                th, td { padding: 5px; }
            </style>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Вес</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''

        # Добавляем строки данных
        for idx, item in enumerate(self.data, 1):
            html_content += f'''
                <tr>
                    <td>{idx}</td>
                    <td>{item['name']}</td>
                    <td>{item['price']}</td>
                    <td>{item['weight']}</td>
                    <td>{item['file']}</td>
                    <td>{item['price_per_kg']:.2f}</td>
                </tr>
            '''

        html_content += '''
            </table>
        </body>
        </html>
        '''

        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Данные успешно экспортированы в {fname}")

    def find_text(self, text):
        """
Ищет товары по фрагменту текста в названии, сортируя их по цене за килограмм.
        """
        self.result = [item for item in self.data if text.lower() in item['name'].lower()]
        self.result = sorted(self.result, key=lambda x: x['price_per_kg'])

        # Определяем максимальную длину названия товара
        self.name_length = max(len(item['name']) for item in self.result) if self.result else 0

        # Печатаем результаты с учётом длины названия
        print(f"\nРезультаты поиска по '{text}':")
        header = f"№     Наименование{' ' * (self.name_length - 10)} Цена   Вес     Файл      Цена за кг."
        print(header)
        for idx, item in enumerate(self.result, 1):
            name_padding = ' ' * (self.name_length - len(item['name']))
            print(
                f"{idx:<5} {item['name']}{name_padding}  {item['price']:<7} {item['weight']:<6} {item['file']:<12} {item['price_per_kg']:.2f}")

        return self.result


# Пример использования класса
pm = PriceMachine()
pm.load_prices()  # Укажите путь к папке, если она отличается от текущей
while True:
    user_input = input("Введите текст для поиска (или 'exit' для выхода): ")
    if user_input.lower() == 'exit':
        print("Работа завершена.")
        break
    pm.find_text(user_input)

# Экспортируем данные в HTML
pm.export_to_html()
