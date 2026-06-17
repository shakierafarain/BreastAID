# 📊 Consultation Notes Feature - Flow Diagram

## Consultation Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONSULTATION WORKFLOW                         │
└─────────────────────────────────────────────────────────────────┘

1. APPOINTMENT REQUEST & APPROVAL
   ┌─────────────────┐
   │ Patient Requests│
   │  Appointment    │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────────┐
   │ Admin Assigns Doctor│
   │ and Schedules Date  │
   └────────┬────────────┘
            │
            ▼
   ┌──────────────────────┐
   │ Doctor & Patient Both│
   │   Accept Appt        │
   └────────┬─────────────┘
            │
            ▼
   ┌─────────────────────┐
   │ Appointment Status: │
   │   "CONFIRMED" ✅    │
   └────────┬────────────┘


2. DURING CONSULTATION
   ┌──────────────────────────┐
   │ Doctor & Patient Chat:   │
   │ - Exchange messages      │
   │ - Discuss symptoms       │
   │ - Share recommendations  │
   └──────────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ When Ready, Doctor │
         │  Clicks: "End      │
         │  Consultation &    │
         │  Write Notes" 📝   │
         └────────┬───────────┘


3. WRITE CONSULTATION NOTES
   ┌────────────────────────────────────────┐
   │ Modal Appears for Doctor to Enter:     │
   │ ┌──────────────────────────────────┐  │
   │ │ • Patient Symptoms & Complaints  │  │
   │ │ • Clinical Observations          │  │
   │ │ • Test Results/Findings          │  │
   │ │ • Diagnosis (if applicable)      │  │
   │ │ • Treatment Plan & Medications   │  │
   │ │ • Follow-up Actions & Referrals  │  │
   │ │ • Important Notes for Future     │  │
   │ └──────────────────────────────────┘  │
   │                                        │
   │ Doctor clicks: "Save & End Consult"  │
   └────────┬─────────────────────────────┘
            │
            ▼
   ┌────────────────────────────┐
   │ Firestore Saves:           │
   │ • Consultation Notes       │
   │ • Appointment Status →     │
   │   "COMPLETED" ✅          │
   │ • Timestamp Created/Updated│
   └────────┬───────────────────┘
            │
            ▼
   ┌────────────────────────────┐
   │ Success! 🎉 Confetti 🎉   │
   │ Notes Are Now Visible      │
   └────────────────────────────┘


4. ACCESS CONSULTATION NOTES

   ┌─────────────────────────────────────────────────┐
   │             DOCTOR ACCESSES NOTES               │
   ├─────────────────────────────────────────────────┤
   │ Click: "📝 Consultation Notes" in Sidebar       │
   │                                                  │
   │ View:                                           │
   │ ├─ My Notes Tab: All notes I wrote              │
   │ │  ├─ Patient Name                              │
   │ │  ├─ Consultation Date                         │
   │ │  ├─ Full Notes                                │
   │ │  └─ "✏️ Edit" Button (can modify)             │
   │ │                                                │
   │ └─ Patient Notes Tab: Notes for my patients     │
   │    ├─ All consultations I did                   │
   │    ├─ Full notes (read-only)                    │
   │    └─ Cannot edit from this tab                 │
   └─────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────┐
   │            PATIENT ACCESSES NOTES               │
   ├─────────────────────────────────────────────────┤
   │ Click: "📝 Consultation Notes" in Sidebar       │
   │                                                  │
   │ View:                                           │
   │ ├─ All Completed Consultations                  │
   │ ├─ Doctor Name & Info                           │
   │ ├─ Consultation Date & Time                     │
   │ ├─ Full Doctor's Notes (READ-ONLY)              │
   │ └─ No Edit Capability (for record integrity)    │
   └─────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────┐
   │             ADMIN ACCESSES NOTES                │
   ├─────────────────────────────────────────────────┤
   │ Click: "📝 Consultation Notes" in Sidebar       │
   │                                                  │
   │ View:                                           │
   │ ├─ ALL Consultation Notes System-Wide           │
   │ ├─ Search by Patient Name/Email                 │
   │ ├─ Search by Doctor Name/Email                  │
   │ ├─ Audit Trail:                                 │
   │ │  ├─ Doctor Name & Email                       │
   │ │  ├─ Patient Name & Email                      │
   │ │  ├─ Consultation Date                         │
   │ │  └─ Full Notes (READ-ONLY)                    │
   │ │                                                │
   │ └─ No Edit Capability (audit integrity)         │
   └─────────────────────────────────────────────────┘
```

## Database Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    FIRESTORE DATABASE                       │
└─────────────────────────────────────────────────────────────┘

COLLECTION: appointments
┌──────────────────────────────────┐
│ Document: appointment_id          │
├──────────────────────────────────┤
│ • public_email                    │
│ • public_name                     │
│ • doctor_email                    │
│ • doctor_name                     │
│ • appointment_date                │
│ • appointment_time                │
│ • status: "confirmed" → "completed"
│ • completed_at: timestamp (NEW)   │
│ • has_notes: true (NEW)           │
│ • meeting_link (if online)        │
└──────────────────────────────────┘
         ↓
      WHEN NOTES SAVED
         ↓
┌──────────────────────────────────┐
│ Updates:                          │
│ • status = "completed"            │
│ • completed_at = datetime.now()   │
│ • has_notes = true                │
└──────────────────────────────────┘


COLLECTION: consultation_notes (NEW)
┌──────────────────────────────────┐
│ Document: auto-generated_id       │
├──────────────────────────────────┤
│ • appointment_id (ref)            │
│ • doctor_email                    │
│ • doctor_name                     │
│ • patient_email                   │
│ • patient_name                    │
│ • notes (text content)            │
│ • created_at (timestamp)          │
│ • updated_at (timestamp)          │
└──────────────────────────────────┘
         ↓
    INDEXED BY:
         ↓
  ┌─────────────────┬────────────┐
  │ appointment_id  │ doctor_email│
  │ patient_email   │             │
  └─────────────────┴────────────┘
```

## Page Navigation Flow

```
SIDEBAR MENU (All Users)
      ↓
  📝 Consultation Notes
      ↓
  ┌────────────────────────────────────────┐
  │  Role-Based Page Loading               │
  └────────────────────────────────────────┘
       │           │            │
       │           │            │
   DOCTOR      PATIENT       ADMIN
       │           │            │
       ▼           ▼            ▼
   ┌─────┐    ┌──────────┐  ┌────────┐
   │Tabs:│    │View All  │  │View All│
   │ • My│    │Notes from│  │Notes   │
   │Notes│    │Doctors   │  │        │
   │     │    │(READ-ONLY)  │(Search)│
   │ • My│    └──────────┘  └────────┘
   │Pat. │
   │ Notes
   └─────┘

EDIT CAPABILITY
      ↓
    DOCTOR: ✅ Can edit own notes
    PATIENT: ❌ Cannot edit (read-only)
    ADMIN:   ❌ Cannot edit (audit mode)
```

## Status Transitions

```
APPOINTMENT STATUS FLOW WITH NOTES:

pending
   ↓
scheduled
   ↓
confirmed (Doctor & Patient both accepted)
   ↓
      ┌────────────────────────┐
      │ Doctor Ends Consult    │
      │ & Writes Notes        │
      └────────┬───────────────┘
             ↓
         COMPLETED ✅
         (with has_notes: true)
         (with completed_at: timestamp)

Consultation notes available in:
• Doctor's "Consultation Notes" page
• Patient's "Consultation Notes" page
• Admin's "Consultation Notes" page (all notes)
```

## User Permission Matrix

```
┌────────────────────────────────────────────────────┐
│              PERMISSION MATRIX                     │
├─────────────────┬──────────┬────────┬──────────────┤
│   Action        │  Doctor  │Patient │ Admin        │
├─────────────────┼──────────┼────────┼──────────────┤
│View Own Notes   │    ✅    │   ✅   │      -       │
│View Patient     │    ✅    │   -    │      ✅      │
│  Notes          │          │        │              │
│View All Notes   │    -     │   -    │      ✅      │
│Edit Own Notes   │    ✅    │   -    │      -       │
│Edit Others      │    -     │   -    │      -       │
│Search Notes     │    -     │   -    │      ✅      │
│Write Notes      │    ✅    │   -    │      -       │
│Delete Notes     │    -     │   -    │      -       │
│Export Notes     │    -     │   -    │      ✅      │
└────────────────┴──────────┴────────┴──────────────┘

✅ = Allowed
-  = Not Allowed
```
