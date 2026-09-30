import math

def calculate(variant, params):
    try:
        if variant == 1:  
            a, b = map(float, params)
            c = math.sqrt(a**2 + b**2)
            return f"Гипотенуза c = {c:.2f}"
        
        elif variant == 2:  
            a, b, c = map(float, params)
            d = b**2 - 4 * a * c
            if d < 0:
                return "Корней нет (D < 0)"
            elif d == 0:
                x = -b / (2 * a)
                return f"Корень x = {x:.2f}"
            else:
                x1 = (-b + math.sqrt(d)) / (2 * a)
                x2 = (-b - math.sqrt(d)) / (2 * a)
                return f"Корни: x1 = {x1:.2f}, x2 = {x2:.2f}"
                
        elif variant == 3:  
            a, b, h = map(float, params)
            s = ((a + b) / 2) * h
            return f"Площадь трапеции S = {s:.2f}"
            
        elif variant == 4:  
            a, h = map(float, params)
            s = a * h
            return f"Площадь параллелограмма S = {s:.2f}"
            
        else:
            return "Неизвестный номер варианта."
    except Exception as e:
        return f"Ошибка при расчёте: {e}"