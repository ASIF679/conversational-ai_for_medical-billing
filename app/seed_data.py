# from app.db.database import SessionLocal
# from app.models.patient import Patient
# from app.models.doctors import Doctor
# from app.models.appointment import Appointment
# from app.models.availability import DoctorAvailability
# from app.models.conversationlogs import Conversation
# import uuid
# from datetime import time, datetime

# def seed():
#     db = SessionLocal()

#     try:
        
#         patient1 = Patient(
#             id=uuid.uuid4(),
#             full_name="Ahmed Raza",
#             phone="03123456789",
#             email="ahmed.raza@example.com"
#         )

#         patient2 = Patient(
#             id=uuid.uuid4(),
#             full_name="Fatima Noor",
#             phone="03219876543",
#             email="fatima.noor@example.com"
#         )

#         db.add_all([patient1, patient2])
#         db.commit()


#         doc1 = Doctor(
#             id=uuid.uuid4(),
#             full_name="Dr. Ali Khan",
#             specialization="Cardiologist",
#             phone="03001234567",
#             email="ali.khan@example.com"
#         )

#         doc2 = Doctor(
#             id=uuid.uuid4(),
#             full_name="Dr. Sara Ahmed",
#             specialization="Dermatologist",
#             phone="03007654321",
#             email="sara.ahmed@example.com"
#         )

#         db.add_all([doc1, doc2])
#         db.commit()

#         availability = [
#             DoctorAvailability(
#                 id=uuid.uuid4(),
#                 doctor_id=doc1.id,
#                 day_of_week=0,  # Monday
#                 start_time=time(9, 0),
#                 end_time=time(14, 0)
#             ),
#             DoctorAvailability(
#                 id=uuid.uuid4(),
#                 doctor_id=doc1.id,
#                 day_of_week=2,  # Wednesday
#                 start_time=time(10, 0),
#                 end_time=time(15, 0)
#             ),
#             DoctorAvailability(
#                 id=uuid.uuid4(),
#                 doctor_id=doc2.id,
#                 day_of_week=1,  # Tuesday
#                 start_time=time(11, 0),
#                 end_time=time(16, 0)
#             ),
#         ]

#         db.add_all(availability)
#         db.commit()

#         appointment1 = Appointment(
#             id=uuid.uuid4(),
#             patient_id=patient1.id,
#             doctor_id=doc1.id,
#             appointment_time=datetime(2026, 4, 25, 10, 0),
#             status="scheduled",
#             reason="Chest pain"
#         )

#         appointment2 = Appointment(
#             id=uuid.uuid4(),
#             patient_id=patient2.id,
#             doctor_id=doc2.id,
#             appointment_time=datetime(2026, 4, 26, 12, 0),
#             status="scheduled",
#             reason="Skin allergy"
#         )

#         db.add_all([appointment1, appointment2])
#         db.commit()

#         convo1 = Conversation(
#             id=uuid.uuid4(),
#             patient_id=patient1.id,
#             channel="web",
#             user_message="I want to book an appointment with a cardiologist",
#             ai_response="Sure, booking an appointment with Dr. Ali Khan.",
#             intent="book_appointment"
#         )

#         convo2 = Conversation(
#             id=uuid.uuid4(),
#             patient_id=patient2.id,
#             channel="web",
#             user_message="Do you have a dermatologist available?",
#             ai_response="Yes, Dr. Sara Ahmed is available.",
#             intent="check_availability"
#         )

#         db.add_all([convo1, convo2])
#         db.commit()

#         print(" Full seed data inserted successfully")

#     except Exception as e:
#         db.rollback()
#         print(" Error:", e)

#     finally:
#         db.close()


# if __name__ == "__main__":
#     seed()


#     -- ═══════════════════════════════════════════════════════════════
# -- 1. DOCTORS
# -- ═══════════════════════════════════════════════════════════════
# INSERT INTO doctors (id, full_name, specialization, phone, email, is_active)
# VALUES 
#     ('11111111-1111-1111-1111-111111111111', 'Dr. Sara Ahmed',    'Dermatologist',     '03001111111', 'sara.ahmed@medcare.com',    true),
#     ('22222222-2222-2222-2222-222222222222', 'Dr. Ali Hassan',    'Cardiologist',      '03002222222', 'ali.hassan@medcare.com',    true),
#     ('33333333-3333-3333-3333-333333333333', 'Dr. Zara Khan',     'Neurologist',       '03003333333', 'zara.khan@medcare.com',     true),
#     ('44444444-4444-4444-4444-444444444444', 'Dr. Omar Sheikh',   'Orthopedic',        '03004444444', 'omar.sheikh@medcare.com',   true),
#     ('55555555-5555-5555-5555-555555555555', 'Dr. Fatima Malik',  'Gynecologist',      '03005555555', 'fatima.malik@medcare.com',  true),
#     ('66666666-6666-6666-6666-666666666666', 'Dr. Bilal Ahmed',   'Pediatrician',      '03006666666', 'bilal.ahmed@medcare.com',   true),
#     ('77777777-7777-7777-7777-777777777777', 'Dr. Ayesha Raza',   'Psychiatrist',      '03007777777', 'ayesha.raza@medcare.com',   true),
#     ('88888888-8888-8888-8888-888888888888', 'Dr. Usman Tariq',   'General Physician', '03008888888', 'usman.tariq@medcare.com',   true);


# -- ═══════════════════════════════════════════════════════════════
# -- 2. DOCTOR AVAILABILITY
# -- day_of_week: 0=Monday 1=Tuesday 2=Wednesday 
# --              3=Thursday 4=Friday 5=Saturday 6=Sunday
# -- ═══════════════════════════════════════════════════════════════
# INSERT INTO doctor_availability (id, doctor_id, day_of_week, start_time, end_time)
# VALUES
#     -- Dr. Sara Ahmed (Dermatologist)
#     (gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 2, '11:00:00', '16:00:00'),  -- Wednesday
#     (gen_random_uuid(), '11111111-1111-1111-1111-111111111111', 4, '09:00:00', '13:00:00'),  -- Friday

#     -- Dr. Ali Hassan (Cardiologist)
#     (gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 0, '10:00:00', '15:00:00'),  -- Monday
#     (gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 3, '14:00:00', '18:00:00'),  -- Thursday

#     -- Dr. Zara Khan (Neurologist)
#     (gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 1, '09:00:00', '12:00:00'),  -- Tuesday
#     (gen_random_uuid(), '33333333-3333-3333-3333-333333333333', 5, '10:00:00', '14:00:00'),  -- Saturday

#     -- Dr. Omar Sheikh (Orthopedic)
#     (gen_random_uuid(), '44444444-4444-4444-4444-444444444444', 2, '08:00:00', '12:00:00'),  -- Wednesday
#     (gen_random_uuid(), '44444444-4444-4444-4444-444444444444', 6, '10:00:00', '15:00:00'),  -- Sunday

#     -- Dr. Fatima Malik (Gynecologist)
#     (gen_random_uuid(), '55555555-5555-5555-5555-555555555555', 1, '13:00:00', '17:00:00'),  -- Tuesday
#     (gen_random_uuid(), '55555555-5555-5555-5555-555555555555', 4, '09:00:00', '13:00:00'),  -- Friday

#     -- Dr. Bilal Ahmed (Pediatrician)
#     (gen_random_uuid(), '66666666-6666-6666-6666-666666666666', 0, '09:00:00', '14:00:00'),  -- Monday
#     (gen_random_uuid(), '66666666-6666-6666-6666-666666666666', 3, '10:00:00', '15:00:00'),  -- Thursday

#     -- Dr. Ayesha Raza (Psychiatrist)
#     (gen_random_uuid(), '77777777-7777-7777-7777-777777777777', 2, '14:00:00', '18:00:00'),  -- Wednesday
#     (gen_random_uuid(), '77777777-7777-7777-7777-777777777777', 5, '09:00:00', '13:00:00'),  -- Saturday

#     -- Dr. Usman Tariq (General Physician)
#     (gen_random_uuid(), '88888888-8888-8888-8888-888888888888', 0, '08:00:00', '16:00:00'),  -- Monday
#     (gen_random_uuid(), '88888888-8888-8888-8888-888888888888', 2, '08:00:00', '16:00:00'),  -- Wednesday
#     (gen_random_uuid(), '88888888-8888-8888-8888-888888888888', 4, '08:00:00', '16:00:00');  -- Friday


# -- ═══════════════════════════════════════════════════════════════
# -- 3. PATIENTS
# -- ═══════════════════════════════════════════════════════════════
# INSERT INTO patients (id, full_name, phone, email)
# VALUES
#     ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Ali Khan',          '03011111111', 'ali.khan@gmail.com'),
#     ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Sara Malik',        '03022222222', 'sara.malik@gmail.com'),
#     ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'Ahmed Raza',        '03033333333', 'ahmed.raza@gmail.com'),
#     ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'Fatima Noor',       '03044444444', 'fatima.noor@gmail.com'),
#     ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'Usman Ghani',       '03055555555', 'usman.ghani@gmail.com'),
#     ('ffffffff-ffff-ffff-ffff-ffffffffffff', 'Zainab Hussain',    '03066666666', 'zainab.h@gmail.com'),
#     ('a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1', 'Bilal Chaudhry',  '03077777777', 'bilal.ch@gmail.com'),
#     ('b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2', 'Hina Baig',       '03088888888', 'hina.baig@gmail.com');


# -- ═══════════════════════════════════════════════════════════════
# -- 4. APPOINTMENTS
# -- ═══════════════════════════════════════════════════════════════
# INSERT INTO appointments 
#     (id, patient_id, doctor_id, appointment_date, appointment_time, reason, status, notes, created_at, updated_at)
# VALUES
#     -- Ali Khan → Dr. Sara Ahmed (Dermatologist) Wednesday
#     (
#         gen_random_uuid(),
#         'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
#         '11111111-1111-1111-1111-111111111111',
#         '2026-05-06', '14:00:00',
#         'Skin rash on arms and neck',
#         'scheduled',
#         NULL,
#         NOW(), NOW()
#     ),
#     -- Sara Malik → Dr. Ali Hassan (Cardiologist) Monday
#     (
#         gen_random_uuid(),
#         'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
#         '22222222-2222-2222-2222-222222222222',
#         '2026-05-11', '11:00:00',
#         'Chest pain and shortness of breath',
#         'scheduled',
#         NULL,
#         NOW(), NOW()
#     ),
#     -- Ahmed Raza → Dr. Zara Khan (Neurologist) Tuesday
#     (
#         gen_random_uuid(),
#         'cccccccc-cccc-cccc-cccc-cccccccccccc',
#         '33333333-3333-3333-3333-333333333333',
#         '2026-05-12', '10:00:00',
#         'Frequent migraines and dizziness',
#         'scheduled',
#         NULL,
#         NOW(), NOW()
#     ),
#     -- Fatima Noor → Dr. Fatima Malik (Gynecologist) Friday
#     (
#         gen_random_uuid(),
#         'dddddddd-dddd-dddd-dddd-dddddddddddd',
#         '55555555-5555-5555-5555-555555555555',
#         '2026-05-08', '10:00:00',
#         'Routine prenatal checkup',
#         'completed',
#         'Patient is in good health. Follow up in 4 weeks.',
#         NOW(), NOW()
#     ),
#     -- Usman Ghani → Dr. Omar Sheikh (Orthopedic) Wednesday
#     (
#         gen_random_uuid(),
#         'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
#         '44444444-4444-4444-4444-444444444444',
#         '2026-05-06', '09:00:00',
#         'Knee pain after sports injury',
#         'scheduled',
#         NULL,
#         NOW(), NOW()
#     ),
#     -- Zainab Hussain → Dr. Bilal Ahmed (Pediatrician) Monday
#     (
#         gen_random_uuid(),
#         'ffffffff-ffff-ffff-ffff-ffffffffffff',
#         '66666666-6666-6666-6666-666666666666',
#         '2026-05-11', '10:00:00',
#         'Child vaccination and growth checkup',
#         'scheduled',
#         NULL,
#         NOW(), NOW()
#     ),
#     -- Bilal Chaudhry → Dr. Ayesha Raza (Psychiatrist) Wednesday
#     (
#         gen_random_uuid(),
#         'a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1',
#         '77777777-7777-7777-7777-777777777777',
#         '2026-05-06', '15:00:00',
#         'Anxiety and sleep disorder consultation',
#         'cancelled',
#         NULL,
#         NOW(), NOW()
#     ),
#     -- Hina Baig → Dr. Usman Tariq (General Physician) Friday
#     (
#         gen_random_uuid(),
#         'b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2',
#         '88888888-8888-8888-8888-888888888888',
#         '2026-05-08', '09:00:00',
#         'Fever and flu symptoms for 3 days',
#         'completed',
#         'Prescribed antibiotics. Rest for 5 days.',
#         NOW(), NOW()
#     );


# -- ═══════════════════════════════════════════════════════════════
# -- 5. CONVERSATIONS
# -- ═══════════════════════════════════════════════════════════════
# INSERT INTO conversations 
#     (id, session_id, patient_id, channel, user_message, ai_response, intent, created_at)
# VALUES
#     -- Session 1: Ali Khan books appointment
#     (
#         gen_random_uuid(),
#         'session-ali-khan-001',
#         'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
#         'web',
#         'Hi I need to see a skin doctor',
#         'Hello! I can help you book an appointment with a Dermatologist. Can I get your phone number to look up your details?',
#         'book_appointment',
#         NOW()
#     ),
#     (
#         gen_random_uuid(),
#         'session-ali-khan-001',
#         'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
#         'web',
#         'My number is 03011111111',
#         'Thank you Ali! I found your record. Dr. Sara Ahmed (Dermatologist) is available on Wednesday 11:00 AM to 4:00 PM and Friday 9:00 AM to 1:00 PM. Which day works for you?',
#         'check_patient',
#         NOW()
#     ),
#     (
#         gen_random_uuid(),
#         'session-ali-khan-001',
#         'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
#         'web',
#         'Wednesday at 2pm please',
#         'Got it! To confirm — Dr. Sara Ahmed on Wednesday May 6th at 2:00 PM. What is the reason for your visit?',
#         'select_slot',
#         NOW()
#     ),
#     (
#         gen_random_uuid(),
#         'session-ali-khan-001',
#         'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
#         'web',
#         'Skin rash on my arms and neck',
#         'Your appointment has been booked successfully! A confirmation email has been sent to ali.khan@gmail.com.',
#         'confirm_booking',
#         NOW()
#     ),

#     -- Session 2: New patient Sara Malik
#     (
#         gen_random_uuid(),
#         'session-sara-malik-001',
#         'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
#         'web',
#         'Hello I need a heart specialist',
#         'Hi! I can help you with that. Let me check availability for a Cardiologist. Can I get your phone number first?',
#         'book_appointment',
#         NOW()
#     ),
#     (
#         gen_random_uuid(),
#         'session-sara-malik-001',
#         'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
#         'web',
#         '03022222222',
#         'Thank you Sara! Dr. Ali Hassan (Cardiologist) is available Monday 10 AM to 3 PM and Thursday 2 PM to 6 PM. Which works for you?',
#         'check_patient',
#         NOW()
#     ),
#     (
#         gen_random_uuid(),
#         'session-sara-malik-001',
#         'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
#         'web',
#         'Monday at 11am',
#         'Your appointment with Dr. Ali Hassan is confirmed for Monday May 11th at 11:00 AM. Confirmation sent to sara.malik@gmail.com.',
#         'confirm_booking',
#         NOW()
#     ),

#     -- Session 3: Anonymous inquiry (no patient yet)
#     (
#         gen_random_uuid(),
#         'session-anonymous-001',
#         NULL,
#         'web',
#         'What specializations do you offer?',
#         'We offer: Dermatology, Cardiology, Neurology, Orthopedics, Gynecology, Pediatrics, Psychiatry, and General Medicine. Which would you like to book?',
#         'general_inquiry',
#         NOW()
#     # )