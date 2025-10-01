import utils.session
import requests
import smtplib
import matplotlib.pyplot as plt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ------------------------- CONFIG -------------------------
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with your key
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Use app password for Gmail security

# ------------------------- WEATHER FETCH -------------------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching weather data")
        return None

# ------------------------- EMAIL ALERT -------------------------
def send_email(receiver_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver_email, msg.as_string())
        server.quit()

        print("Email alert sent successfully!")
    except Exception as e:
        print("Error sending email:", e)

# ------------------------- DATA PROCESSING -------------------------
def process_weather(data, user_email, city):
    temps, humidity, rainfall, dates = [], [], [], []
    rain_alert = False

    for forecast in data['list'][:8]:  # next ~24 hours
        dt = datetime.fromtimestamp(forecast['dt'])
        temp = forecast['main']['temp']
        hum = forecast['main']['humidity']
        rain = forecast.get('rain', {}).get('3h', 0)

        temps.append(temp)
        humidity.append(hum)
        rainfall.append(rain)
        dates.append(dt.strftime('%H:%M'))

        if rain > 0:
            rain_alert = True

    # Visualization
    plt.figure(figsize=(10, 6))
    plt.plot(dates, temps, label='Temperature (°C)', marker='o')
    plt.plot(dates, humidity, label='Humidity (%)', marker='s')
    plt.plot(dates, rainfall, label='Rainfall (mm)', marker='^')
    plt.title(f"Weather Trends for {city}")
    plt.xlabel("Time")
    plt.ylabel("Values")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Send alert if rain expected
    if rain_alert:
        subject = f"Weather Alert: Rain expected in {city}"
        body = f"Hello!\n\nRain is expected in {city} within the next 24 hours. Don't forget to carry an umbrella! ☔\n\nRegards,\nWeather Bot"
        send_email(user_email, subject, body)
    else:
        print("No rain expected in the next 24 hours.")

# ------------------------- MAIN -------------------------
if __name__ == "__main__":
    user_city = input("Enter your city: ")
    user_email = input("Enter your email for alerts: ")

    weather_data = get_weather(user_city)
    if weather_data:
        process_weather(weather_data, user_email, user_city)
