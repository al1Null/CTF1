PROGRAM plc2
  VAR
    ColorSensor_RED AT %QW0 : INT;
    ColorSensor_GREEN AT %QW1 : INT;
    ColorSensor_BLUE AT %QW2 : INT;
    RangeSensor AT %MD0 : REAL := 100.0;
    Pump AT %QX0.4 : BOOL := FALSE;
    Doser_RED AT %QX0.6 : BOOL := FALSE;
    Doser_BLUE AT %QX0.7 : BOOL := FALSE;
  END_VAR
  VAR
    settleTime : TIME := TIME#5s;
    doseTime : TIME := TIME#1s;
    shutDown : BOOL := FALSE;
    treatmentComplete : BOOL := FALSE;
  END_VAR
  VAR
    stage AT %QW5 : INT := 0;
    desiredDistanceFill AT %MD1 : REAL := 60.0;
  END_VAR
  VAR
    minRed : INT := 20;
    doseTimer : TON;
    settleTimer : TON;
  END_VAR

  CASE stage OF
      0:  (*Filling stage: it will fill up to a certain amount that corresponds to a certain distance*)
      
          IF RangeSensor > desiredDistanceFill THEN
            Pump := TRUE;
          ELSE
            Pump := FALSE;
            stage := 1;
          END_IF;
          
     1:  (*Treatment stage*)
      
          IF ColorSensor_RED < minRed THEN (*Ensure minimum red value is inserted*)
            stage := 2;
            Doser_RED := TRUE;
            doseTimer(IN:= NOT doseTimer.Q, PT:= doseTime);
            
          ELSIF ColorSensor_RED > ColorSensor_BLUE  THEN (*Ensure blue quantity is > Red *)
            
              stage := 3;
              Doser_BLUE := TRUE;
              doseTimer(IN:= NOT doseTimer.Q, PT:= doseTime);
          
          ELSE  (*Treatment complete*)
            
            stage := 5;
            
          END_IF;
          
      2:  (*Red Dosing Stage*)
      
          IF doseTimer.Q THEN
            Doser_RED := FALSE;
            stage := 4;
            doseTimer(IN:= FALSE);
            settleTimer(IN:= NOT settleTimer.Q, PT:= settleTime); (*let the dose settle*)
          END_IF;
          
      3: (* Blue Dosing Stage*)
      
          IF doseTimer.Q THEN
            Doser_BLUE := FALSE;
            stage := 4;
            doseTimer(IN:= FALSE);
            settleTimer(IN:= NOT settleTimer.Q, PT:= settleTime); (*let the dose settle*)
          END_IF;
          
      4: (*Settling Stage for Dosage*)
      
          IF settleTimer.Q THEN
          stage := 1;
          settleTimer(IN:=FALSE);
          END_IF;
      
      5: (*Treatment Complete*)
      
        treatmentComplete := TRUE;
        
  END_CASE;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#200ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : plc2;
  END_RESOURCE
END_CONFIGURATION
