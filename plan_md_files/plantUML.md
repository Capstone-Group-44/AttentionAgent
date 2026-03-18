@startuml
title Distraction Notifier - Refined System Architecture

actor User
participant "User Interface (UI)" as UI


    participant "FocusTrackingWorker\n(ML Engine)" as MLE
    participant "DB Modifier" as DAO
    database "Local SQLite DB" as DB
    participant "DistractionNotifierWorker" as DN


participant "Notification Service" as NS
database "External System: Firestore" as FS

== Session Start ==
User -> UI: Press "Start Session"
activate UI

par Parallel Initialization
    UI -> MLE: run() loop
    activate MLE
    UI -> DN: run() loop
    activate DN
end
deactivate UI

== Continuous Processing ==
loop While Session Active
    
    group ML Data Ingestion
        MLE -> MLE: Predict Focus State
        MLE -> DAO: insert_sample()
        activate DAO
        DAO -> DB: SQL INSERT
        deactivate DAO
        
        MLE -> FS: _push_sample_to_firestore()
    end

    group Distraction Polling (Every 20s)
        DN -> DN: sleep(20s)
        
        DN -> DAO: get_recent_attention_states(window=20s)
        activate DAO
        DAO -> DB: SELECT attention_states
        DB --> DAO: ResultSet
        deactivate DAO
        DAO --> DN: List of states [0, 1, 0...]

        alt "Distracted / Total > 0.50"
            DN -> NS: send_notification()
            NS -> User: OS-Native Popup
            
            note over DN: Cooldown Lockout (60s)
            DN -> DN: sleep(60s)
        else "Focused"
            note right of DN: Wait next 20s cycle
        end
    end

end

@enduml