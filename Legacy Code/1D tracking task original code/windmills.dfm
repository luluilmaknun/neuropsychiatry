object Main: TMain
  Left = 0
  Top = 0
  Width = 1444
  Height = 857
  Caption = 'Tracking task'
  Color = clSilver
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  OldCreateOrder = False
  OnClose = FormClose
  OnCreate = FormCreate
  PixelsPerInch = 96
  TextHeight = 13
  object Sample_Count: TLabel
    Left = 1288
    Top = 184
    Width = 11
    Height = 22
    Caption = '0'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -19
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
  end
  object Record_Light: TShape
    Left = 1264
    Top = 32
    Width = 57
    Height = 57
    Brush.Color = clMaroon
    Pen.Style = psClear
    Shape = stCircle
  end
  object Trial_Count: TLabel
    Left = 1288
    Top = 120
    Width = 15
    Height = 32
    Caption = '0'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clBlue
    Font.Height = -27
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
  end
  object Label1: TLabel
    Left = 1152
    Top = 48
    Width = 95
    Height = 24
    Caption = 'Recording'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
  end
  object Label2: TLabel
    Left = 1152
    Top = 128
    Width = 115
    Height = 24
    Caption = 'Trial counter'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
  end
  object Label3: TLabel
    Left = 1152
    Top = 184
    Width = 109
    Height = 18
    Caption = 'Sample counter'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -16
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
  end
  object fixation: TShape
    Left = 488
    Top = 488
    Width = 24
    Height = 24
    Brush.Color = clBlue
    Pen.Style = psClear
    Shape = stCircle
    Visible = False
  end
  object Task_Panel: TPanel
    Left = -272
    Top = 28
    Width = 1000
    Height = 1000
    BorderStyle = bsSingle
    Color = clBlack
    TabOrder = 0
    Visible = False
    object Score_Display: TLabel
      Left = 248
      Top = 248
      Width = 444
      Height = 299
      Caption = '100'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clLime
      Font.Height = -267
      Font.Name = 'Arial'
      Font.Style = []
      ParentFont = False
    end
    object Target3: TShape
      Left = 432
      Top = 608
      Width = 120
      Height = 120
      Brush.Color = clRed
      Pen.Color = clRed
      Pen.Style = psClear
    end
    object Target2: TShape
      Left = 448
      Top = 616
      Width = 120
      Height = 120
      Brush.Color = clRed
      Pen.Color = clRed
      Pen.Style = psClear
    end
    object Target: TShape
      Left = 448
      Top = 616
      Width = 120
      Height = 120
      Brush.Color = clRed
      Pen.Color = clRed
      Pen.Style = psClear
    end
    object Cursor: TShape
      Left = 384
      Top = 80
      Width = 120
      Height = 120
      Brush.Color = clYellow
      Pen.Style = psClear
    end
    object Cursor2: TShape
      Left = 392
      Top = 88
      Width = 120
      Height = 120
      Brush.Color = clYellow
      Pen.Style = psClear
    end
  end
  object StartStop: TButton
    Left = 1208
    Top = 328
    Width = 121
    Height = 49
    Caption = 'Start'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
    TabOrder = 1
    OnClick = StartStopClick
  end
  object Zero_Button: TButton
    Left = 1208
    Top = 392
    Width = 121
    Height = 49
    Caption = 'Zero'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
    TabOrder = 2
    OnClick = Zero_ButtonClick
  end
  object Record_On: TCheckBox
    Left = 1208
    Top = 480
    Width = 113
    Height = 41
    Caption = 'Record'
    Checked = True
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
    State = cbChecked
    TabOrder = 3
  end
  object Filename_Edit: TEdit
    Left = 1208
    Top = 584
    Width = 81
    Height = 26
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -16
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
    TabOrder = 4
    Text = 'test'
  end
  object Pathname_Edit: TEdit
    Left = 1208
    Top = 544
    Width = 113
    Height = 26
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -16
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
    TabOrder = 5
    Text = 'D:\MCIdata'
  end
  object ID_Edit: TEdit
    Left = 1296
    Top = 584
    Width = 25
    Height = 26
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -16
    Font.Name = 'Arial'
    Font.Style = []
    ParentFont = False
    TabOrder = 6
    Text = '1'
    OnChange = ID_EditChange
  end
  object Task_Timer: TTimer
    Enabled = False
    Interval = 1
    OnTimer = Task_TimerTimer
    Left = 1280
    Top = 256
  end
end
