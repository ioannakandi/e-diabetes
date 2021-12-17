glucose=int(input('Type your current glucose level or type "0" for not having measured it yet\t'))
if  (glucose==0 or glucose>300):
    print("this answer will not be taken into account\t")
elif (glucose>=120 or glucose<200):
        print("Eat healthy and measure it again after 4 hours\t", glucose)
elif (glucose>=200 or glucose<=300):
    print("Talk with your doctor\t" , glucose)
else:
    print("Your glucose level is ok\t", glucose)

BloodPressure=int(input('Tell me your current BloodPressure or type "0" for not having measured it yet\t'))
if BloodPressure ==0 or BloodPressure>=200 :
    print("this answer will not be taken into account\t")
elif BloodPressure>=80 or BloodPressure<90 :
    print("Your BloodPressure is ok but you should keep eating healthy")
elif (BloodPressure>=90):
    print("You have hypertasis\t", BloodPressure)
else:
    print("Your Bloodpressure level is ok\t", BloodPressure)

bmi=float(input('Type your current bmi level or type "0" for not having measured it yet\t'))
if (bmi==0 or bmi>100):
    print("this answer will not be taken into account\t")
elif (bmi>0 or bmi<20)
    print("You are underweight\t", bmi)
elif (bmi>=20 or bmi<25):
    print("Your is bmi is good\t", bmi)
elif (bmi>=25 or bmi<30):
    print("You are overweight\t", bmi)
else:
    print("You are obese\t", bmi)

age=int(input("Type your age"))
if age>=0 or age<=120:
    print("Your age is\t", age)
else:
    print("this answer will not be taken into account\t")

insulin=int(input('Type your insulin level two hours after glucose administration or type "0" for not having measured it yet'))
if insulin==0 or insulin>=900:
    print ("this answer will not be taken into account\t")
elif insulin<16:
    print("You have hypoglycemia\t", insulin)
elif insulin>166:
    print("You have hyperglycemia\t", insulin)
else:
    print("Your insulin level is good")
