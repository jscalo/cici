from twilio.rest import Client

# Your Account SID from twilio.com/console
accountSID = "<your-account-sid>"
# Your Auth Token from twilio.com/console
authToken = "<your-auth-token>"

fromPhNum = "<your-twilio-phone-number>"

client = Client(accountSID, authToken)
phNum = None

def sendSMS(message):
    response = client.messages.create(to=phNum, from_=fromPhNum, body=message)
