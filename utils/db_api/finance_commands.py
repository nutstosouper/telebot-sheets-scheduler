
import logging
import datetime
from . import google_sheets
from . import service_commands
from . import appointment_commands
from . import user_commands

async def add_service_costs(service_id, materials_cost, time_cost, other_costs):
    """Add or update service costs"""
    try:
        # Get existing service costs
        costs_data = await google_sheets.get_sheet("ServiceCosts")
        
        # Check if service cost already exists
        existing_cost = None
        for cost in costs_data:
            if str(cost["service_id"]) == str(service_id):
                existing_cost = cost
                break
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if existing_cost:
            # Update existing cost
            existing_cost["materials_cost"] = materials_cost
            existing_cost["time_cost"] = time_cost
            existing_cost["other_costs"] = other_costs
            existing_cost["last_updated"] = now
            
            # Write back to sheet
            success = await google_sheets.write_to_sheet("ServiceCosts", costs_data)
        else:
            # Create new cost entry
            new_cost = {
                "service_id": service_id,
                "materials_cost": materials_cost,
                "time_cost": time_cost,
                "other_costs": other_costs,
                "last_updated": now
            }
            costs_data.append(new_cost)
            
            # Write back to sheet
            success = await google_sheets.write_to_sheet("ServiceCosts", costs_data)
        
        return success
    except Exception as e:
        logging.error(f"Error adding/updating service costs: {str(e)}")
        return False

async def get_service_costs(service_id):
    """Get costs for a specific service"""
    try:
        costs_data = await google_sheets.get_sheet("ServiceCosts")
        
        for cost in costs_data:
            if str(cost["service_id"]) == str(service_id):
                return cost
        
        # Return default if not found
        return {
            "service_id": service_id,
            "materials_cost": 0,
            "time_cost": 0,
            "other_costs": 0,
            "last_updated": ""
        }
    except Exception as e:
        logging.error(f"Error getting service costs: {str(e)}")
        return None

async def calculate_service_profit(service_id):
    """Calculate profit for a specific service"""
    try:
        # Get service details
        service = await service_commands.get_service(service_id)
        if not service:
            return None
        
        # Get service costs
        costs = await get_service_costs(service_id)
        if not costs:
            return {
                "service_id": service_id,
                "service_name": service["name"],
                "price": service["price"],
                "total_cost": 0,
                "profit": service["price"],
                "margin_percent": 100
            }
        
        # Calculate profit metrics
        total_cost = float(costs["materials_cost"]) + float(costs["time_cost"]) + float(costs["other_costs"])
        profit = float(service["price"]) - total_cost
        
        # Calculate margin percentage (avoid division by zero)
        margin_percent = 0
        if float(service["price"]) > 0:
            margin_percent = round((profit / float(service["price"])) * 100, 2)
        
        return {
            "service_id": service_id,
            "service_name": service["name"],
            "price": service["price"],
            "total_cost": total_cost,
            "profit": profit,
            "margin_percent": margin_percent
        }
    except Exception as e:
        logging.error(f"Error calculating service profit: {str(e)}")
        return None

async def add_daily_analytics(admin_id, date, total_income, total_expenses, appointments_count):
    """Add daily financial analytics"""
    try:
        analytics_data = await google_sheets.get_sheet("FinanceAnalytics")
        
        # Check if entry for this date already exists
        existing_entry = None
        for entry in analytics_data:
            if str(entry["admin_id"]) == str(admin_id) and entry["date"] == date:
                existing_entry = entry
                break
        
        profit = total_income - total_expenses
        
        if existing_entry:
            # Update existing entry
            existing_entry["total_income"] = total_income
            existing_entry["total_expenses"] = total_expenses
            existing_entry["profit"] = profit
            existing_entry["appointments_count"] = appointments_count
            
            # Write back to sheet
            success = await google_sheets.write_to_sheet("FinanceAnalytics", analytics_data)
        else:
            # Create new entry
            new_entry = {
                "admin_id": admin_id,
                "date": date,
                "total_income": total_income,
                "total_expenses": total_expenses,
                "profit": profit,
                "appointments_count": appointments_count
            }
            analytics_data.append(new_entry)
            
            # Write back to sheet
            success = await google_sheets.write_to_sheet("FinanceAnalytics", analytics_data)
        
        return success
    except Exception as e:
        logging.error(f"Error adding daily analytics: {str(e)}")
        return False

async def get_analytics_period(admin_id, start_date, end_date):
    """Get analytics for a specific period"""
    try:
        analytics_data = await google_sheets.get_sheet("FinanceAnalytics")
        
        # Filter data by admin_id and date range
        filtered_data = []
        for entry in analytics_data:
            if str(entry["admin_id"]) == str(admin_id) and entry["date"] >= start_date and entry["date"] <= end_date:
                filtered_data.append(entry)
        
        # Calculate totals
        total_income = sum(float(entry["total_income"]) for entry in filtered_data)
        total_expenses = sum(float(entry["total_expenses"]) for entry in filtered_data)
        total_profit = sum(float(entry["profit"]) for entry in filtered_data)
        total_appointments = sum(int(entry["appointments_count"]) for entry in filtered_data)
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_profit": total_profit,
            "total_appointments": total_appointments,
            "daily_data": filtered_data
        }
    except Exception as e:
        logging.error(f"Error getting analytics for period: {str(e)}")
        return None

async def update_client_stats(client_id, service_id=None, amount=0):
    """Update client statistics"""
    try:
        client_stats_data = await google_sheets.get_sheet("ClientStats")
        client_appointments = await appointment_commands.get_client_appointments(client_id)
        client = await user_commands.get_user(client_id)
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Check if client already has stats
        existing_stats = None
        for stats in client_stats_data:
            if str(stats["client_id"]) == str(client_id):
                existing_stats = stats
                break
        
        # Count service occurrences to find favorite
        service_count = {}
        total_spent = 0
        
        for appt in client_appointments:
            service = await service_commands.get_service(appt["service_id"])
            if service:
                service_id = appt["service_id"]
                service_count[service_id] = service_count.get(service_id, 0) + 1
                total_spent += float(service["price"])
        
        # Find most common service
        favorite_service = ""
        max_count = 0
        for s_id, count in service_count.items():
            if count > max_count:
                max_count = count
                service = await service_commands.get_service(s_id)
                favorite_service = service["name"] if service else ""
        
        # Determine if VIP (more than 10 appointments or spent more than 15000)
        vip_status = "Yes" if len(client_appointments) > 10 or total_spent > 15000 else "No"
        
        if existing_stats:
            # Update existing stats
            existing_stats["total_visits"] = len(client_appointments)
            existing_stats["total_spent"] = total_spent
            existing_stats["last_visit"] = today
            existing_stats["favorite_service"] = favorite_service
            existing_stats["vip_status"] = vip_status
            
            # Write back to sheet
            success = await google_sheets.write_to_sheet("ClientStats", client_stats_data)
        else:
            # Create new stats entry
            new_stats = {
                "client_id": client_id,
                "total_visits": len(client_appointments),
                "total_spent": total_spent,
                "last_visit": today,
                "favorite_service": favorite_service,
                "vip_status": vip_status,
                "notes": ""
            }
            client_stats_data.append(new_stats)
            
            # Write back to sheet
            success = await google_sheets.write_to_sheet("ClientStats", client_stats_data)
        
        return success
    except Exception as e:
        logging.error(f"Error updating client stats: {str(e)}")
        return False

async def get_client_stats(client_id):
    """Get client statistics"""
    try:
        client_stats_data = await google_sheets.get_sheet("ClientStats")
        
        for stats in client_stats_data:
            if str(stats["client_id"]) == str(client_id):
                return stats
        
        # Return default stats if not found
        return {
            "client_id": client_id,
            "total_visits": 0,
            "total_spent": 0,
            "last_visit": "",
            "favorite_service": "",
            "vip_status": "No",
            "notes": ""
        }
    except Exception as e:
        logging.error(f"Error getting client stats: {str(e)}")
        return None

async def get_vip_clients():
    """Get list of VIP clients"""
    try:
        client_stats_data = await google_sheets.get_sheet("ClientStats")
        
        vip_clients = []
        for stats in client_stats_data:
            if stats["vip_status"] == "Yes":
                client = await user_commands.get_user(stats["client_id"])
                if client:
                    vip_clients.append({
                        "client_id": stats["client_id"],
                        "name": client.get("full_name", "Unknown"),
                        "total_visits": stats["total_visits"],
                        "total_spent": stats["total_spent"]
                    })
        
        return vip_clients
    except Exception as e:
        logging.error(f"Error getting VIP clients: {str(e)}")
        return []

async def get_service_popularity():
    """Get popularity ranking of services"""
    try:
        appointments = await appointment_commands.get_all_appointments()
        services = await service_commands.get_all_services()
        
        service_counts = {}
        service_revenue = {}
        
        for appt in appointments:
            service_id = appt["service_id"]
            service_counts[service_id] = service_counts.get(service_id, 0) + 1
            
            # Calculate revenue
            service = next((s for s in services if str(s["id"]) == str(service_id)), None)
            if service:
                price = float(service.get("price", 0))
                service_revenue[service_id] = service_revenue.get(service_id, 0) + price
        
        # Create popularity ranking
        popularity_data = []
        for service in services:
            service_id = service["id"]
            count = service_counts.get(service_id, 0)
            revenue = service_revenue.get(service_id, 0)
            
            popularity_data.append({
                "service_id": service_id,
                "name": service["name"],
                "appointment_count": count,
                "total_revenue": revenue,
                "average_price": service.get("price", 0)
            })
        
        # Sort by appointment count (descending)
        popularity_data.sort(key=lambda x: x["appointment_count"], reverse=True)
        
        return popularity_data
    except Exception as e:
        logging.error(f"Error getting service popularity: {str(e)}")
        return []

async def calculate_profit_forecast(admin_id, days=30):
    """Calculate profit forecast for the next X days"""
    try:
        # Get historical data for the past 30 days
        today = datetime.datetime.now()
        past_start = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        past_end = today.strftime("%Y-%m-%d")
        
        past_data = await get_analytics_period(admin_id, past_start, past_end)
        
        if not past_data or past_data["total_appointments"] == 0:
            return {
                "forecast_days": days,
                "estimated_income": 0,
                "estimated_expenses": 0,
                "estimated_profit": 0,
                "confidence": "low"
            }
        
        # Calculate daily averages
        days_with_data = len(past_data["daily_data"])
        if days_with_data == 0:
            days_with_data = 1  # Avoid division by zero
            
        avg_daily_income = past_data["total_income"] / days_with_data
        avg_daily_expenses = past_data["total_expenses"] / days_with_data
        avg_daily_profit = past_data["total_profit"] / days_with_data
        
        # Calculate projections
        forecast_income = avg_daily_income * days
        forecast_expenses = avg_daily_expenses * days
        forecast_profit = avg_daily_profit * days
        
        # Determine confidence level
        confidence = "medium"
        if days_with_data < 7:
            confidence = "low"
        elif days_with_data > 21:
            confidence = "high"
        
        return {
            "forecast_days": days,
            "estimated_income": round(forecast_income, 2),
            "estimated_expenses": round(forecast_expenses, 2),
            "estimated_profit": round(forecast_profit, 2),
            "confidence": confidence
        }
    except Exception as e:
        logging.error(f"Error calculating profit forecast: {str(e)}")
        return None

async def get_daily_forecast_message(admin_id):
    """Get personalized daily forecast message"""
    try:
        # Get forecast for the next 30 days
        forecast = await calculate_profit_forecast(admin_id)
        if not forecast:
            return "Недостаточно данных для прогноза."
        
        # Get service popularity
        popular_services = await get_service_popularity()
        top_service = popular_services[0] if popular_services else None
        
        # Get weekday stats
        appointments = await appointment_commands.get_all_appointments()
        
        weekday_counts = [0, 0, 0, 0, 0, 0, 0]  # Sun, Mon, ... Sat
        
        for appt in appointments:
            try:
                date_obj = datetime.datetime.strptime(appt["date"], "%Y-%m-%d")
                weekday = date_obj.weekday()
                weekday_counts[weekday] += 1
            except:
                pass
        
        # Find least busy day
        min_count = min(weekday_counts[:5])  # Exclude weekend
        least_busy_day_index = weekday_counts.index(min_count)
        days = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу", "воскресенье"]
        least_busy_day = days[least_busy_day_index]
        
        # Build personalized message
        message = f"📊 *Финансовый прогноз на ближайшие 30 дней*\n\n"
        message += f"Ожидаемый доход: {forecast['estimated_income']} руб.\n"
        message += f"Ожидаемые расходы: {forecast['estimated_expenses']} руб.\n"
        message += f"Ожидаемая прибыль: {forecast['estimated_profit']} руб.\n\n"
        
        if top_service:
            message += f"🏆 Самая популярная услуга: {top_service['name']} (заказов: {top_service['appointment_count']})\n\n"
        
        message += f"💡 Рекомендация: У вас меньше всего записей в {least_busy_day}. "
        message += f"Попробуйте запустить акцию в этот день, чтобы привлечь больше клиентов."
        
        return message
    except Exception as e:
        logging.error(f"Error generating forecast message: {str(e)}")
        return "Произошла ошибка при формировании прогноза."

async def update_client_note(client_id, note):
    """Update note for a specific client"""
    try:
        client_stats_data = await google_sheets.get_sheet("ClientStats")
        
        # Check if client already has stats
        existing_stats = None
        for stats in client_stats_data:
            if str(stats["client_id"]) == str(client_id):
                existing_stats = stats
                break
        
        if existing_stats:
            # Update existing note
            existing_stats["notes"] = note
            
            # Write back to sheet
            success = await google_sheets.write_to_sheet("ClientStats", client_stats_data)
            return success
        else:
            # Create new stats entry with note
            await update_client_stats(client_id)  # Create base stats
            
            # Now add the note
            return await update_client_note(client_id, note)
    except Exception as e:
        logging.error(f"Error updating client note: {str(e)}")
        return False
