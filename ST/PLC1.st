PROGRAM plc1
  VAR
    ColorSensor_RED AT %IW0 : INT;
    ColorSensor_GREEN AT %IW1 : INT;
    ColorSensor_BLUE AT %IW2 : INT;
    RangeSensor AT %IW3 : INT;
    Pump AT %QX0.4 : BOOL := False;
    treatmentComplete AT %IX100.0 : BOOL := False;
  END_VAR
  VAR
    desiredDistanceFill : REAL := 7.0;
    measuredDistance : REAL;
  END_VAR


  (*Workaround to distance measure bug*)
  measuredDistance := INT_TO_REAL(RangeSensor)/100.0;
  desiredDistanceFill := 7.0;

  IF treatmentComplete THEN
          IF measuredDistance > desiredDistanceFill THEN
            Pump := False;
          ELSE
            Pump := True;
          END_IF;
  END_IF;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : plc1;
  END_RESOURCE
END_CONFIGURATION
