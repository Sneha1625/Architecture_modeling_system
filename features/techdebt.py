def calculate_technical_debt(parsed_files):

    total_functions = 0
    total_classes = 0
    complexity_penalty = 0
    long_function_penalty = 0

    for parsed in parsed_files:

        functions = parsed.get("functions", [])
        classes = parsed.get("classes", [])

        total_functions += len(functions)
        total_classes += len(classes)

        for func in functions:

            complexity = func.get("complexity", 1)
            lines = func.get("lines", 0)

            # 🔴 High complexity penalty
            if complexity > 10:
                complexity_penalty += 2   # 2 hours

            # 🔴 Long function penalty
            if lines > 50:
                long_function_penalty += 1.5  # 1.5 hours

    # 🧮 Base estimates
    base_time = total_functions * 0.5   # 30 min per function
    class_time = total_classes * 1      # 1 hour per class

    total_hours = base_time + class_time + complexity_penalty + long_function_penalty

    # 💰 Cost estimation (optional)
    hourly_rate = 500  # ₹ per hour (you can change)
    total_cost = total_hours * hourly_rate

    return {
        "functions": total_functions,
        "classes": total_classes,
        "estimated_hours": round(total_hours, 2),
        "estimated_cost": round(total_cost, 2),
        "complexity_penalty": complexity_penalty,
        "long_function_penalty": long_function_penalty
    }