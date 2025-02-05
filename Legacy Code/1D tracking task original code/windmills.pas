unit windmills;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Buttons, ExtCtrls, Math, usetone, nidaqmx, nidaqmxcapi_tlb;

const
  max_delay=1;          {Make sure this is GREATER (not equal to) your maximum delay condition}
  list_len=8;           {Make sure this equals the number of conditions defined below}
  track_time=10;        {The length of trials in seconds}
  screen_size=800;
  start_phase=1;
  track_phase=2;
  score_phase=3;
  rest_phase=4;
  end_phase=5;
  radius=200;
  clock_freq=50;
  delay_buf_len=round(max_delay*clock_freq);
  dac_buf_len=10000;
  smooth_const=80;
  score_const=0.5;
  sample_rate_hi=5000;
  num_chan=1;
  buflen_hi=num_chan*sample_rate_hi;
  num_lo=9;
  buflen_lo=100*num_lo;
  cursor_scale=100;

type
  trial_type = record
    target_freq:real;
    target_amp:real;
    cursor_freq:real;
    cursor_amp:real;
    delay:real;
    cond:integer;
    end;
  TMain = class(TForm)
    Task_Panel: TPanel;
    StartStop: TButton;
    Task_Timer: TTimer;
    Score_Display: TLabel;
    Sample_Count: TLabel;
    Zero_Button: TButton;
    Target3: TShape;
    Target2: TShape;
    Target: TShape;
    Cursor: TShape;
    Cursor2: TShape;
    Record_On: TCheckBox;
    Filename_Edit: TEdit;
    Pathname_Edit: TEdit;
    ID_Edit: TEdit;
    Record_Light: TShape;
    Trial_Count: TLabel;
    Label1: TLabel;
    Label2: TLabel;
    Label3: TLabel;
    fixation: TShape;
    procedure FormCreate(Sender: TObject);
    procedure StartStopClick(Sender: TObject);
    procedure Task_TimerTimer(Sender: TObject);
    procedure Zero_ButtonClick(Sender: TObject);
    procedure ID_EditChange(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  Main: TMain;
  dac_data:array[1..dac_buf_len,1..num_chan] of double;
  buf_hi:array[0..buflen_hi-1] of smallint;
  buf_lo:array[0..buflen_hi-1] of smallint;
  data_lo:array[1..num_lo] of smallint;
  curhalf_hi,curhalf_lo:integer;
  conta:integer;
  fid_hi,fid_lo:thandle;
  fn_hi,fn_lo:string;
  ov_hi,ov_lo:toverlapped;
  fileoffset_hi,fileoffset_lo,pointer_hi,pointer_lo,id:integer;
  trial_list:array[1..list_len] of trial_type;
  task_on,zeroed:boolean;
  current_phase,phase_time,next_phase_time:integer;
  trial_counter,list_counter,norm_score,score_count:integer;
  target_theta,target2_theta,target3_theta,target_freq,current_score,total_score:real;
  daqhandle,dighandle,dighandle2:longint;
  target_pos,target2_pos,target3_pos,cursor_pos,cursor2_pos:array[1..2] of real;
  cursor_buf:array[0..delay_buf_len,1..2] of real;
  delay_len:array[1..2] of integer;
  delay_pointer:integer;
  target_move:boolean;
  stimline:array[0..5] of byte;
  ft_val,ft_zero:array[1..num_chan] of real;
  rand_delay:integer;
  pert:array[1..2] of real;
  set_freq,set_amp:real;

implementation

{$R *.dfm}

procedure set_vfb(c_fb,t_fb,f_fb:boolean);
begin
  Main.Cursor.Visible:=c_fb;
  Main.Cursor2.Visible:=c_fb;
  Main.Target.Visible:=t_fb;
  Main.Target2.Visible:=false;
  Main.Target3.Visible:=false;
 { Main.fixation.Visible:=f_fb   }
end;

procedure init_new_list;
var f,p,i,j:integer;
  temp:trial_type;
begin

{Define your trials here. For each trial give:

target_freq - frequency of target motion in Hz
target_amp - amplitude of target motion (full range is 1)
cursor_freq - frequency of perturbation applied to the cursor in Hz
cursor_amp - amplitude of cursor perturbation
delay - time delay in seconds
}

  trial_list[1].target_freq:=0.1;trial_list[1].target_amp:=1;trial_list[1].cursor_freq:=0;trial_list[1].cursor_amp:=0;trial_list[1].delay:=0;
  trial_list[2].target_freq:=0.2;trial_list[2].target_amp:=1;trial_list[2].cursor_freq:=0;trial_list[2].cursor_amp:=0;trial_list[2].delay:=0;
  trial_list[3].target_freq:=0;trial_list[3].target_amp:=0;trial_list[3].cursor_freq:=0.1;trial_list[3].cursor_amp:=1;trial_list[3].delay:=0;
  trial_list[4].target_freq:=0;trial_list[4].target_amp:=0;trial_list[4].cursor_freq:=0.2;trial_list[4].cursor_amp:=1;trial_list[4].delay:=0;
  trial_list[5].target_freq:=0.1;trial_list[5].target_amp:=1;trial_list[5].cursor_freq:=0;trial_list[5].cursor_amp:=0;trial_list[5].delay:=0.4;
  trial_list[6].target_freq:=0.2;trial_list[6].target_amp:=1;trial_list[6].cursor_freq:=0;trial_list[6].cursor_amp:=0;trial_list[6].delay:=0.4;
  trial_list[7].target_freq:=0;trial_list[7].target_amp:=0;trial_list[7].cursor_freq:=0.1;trial_list[7].cursor_amp:=1;trial_list[7].delay:=0.4;
  trial_list[8].target_freq:=0;trial_list[8].target_amp:=0;trial_list[8].cursor_freq:=0.2;trial_list[8].cursor_amp:=1;trial_list[8].delay:=0.4;

  for i:=1 to list_len do
   trial_list[i].cond:=i;

  for i:=1 to list_len do
    begin
      temp:=trial_list[i];
      j:=RandomRange(i,list_len);
      trial_list[i]:=trial_list[j];
      trial_list[j]:=temp
    end;
  list_counter:=1;
end;

procedure init_new_trial;
var s:string;
begin
  trial_counter:=trial_counter+1;
  str(trial_counter,s);
  Main.Trial_Count.Caption:=s;
  list_counter:=list_counter+1;
  if list_counter>list_len then init_new_list;
  current_phase:=start_phase;
  set_vfb(true,true,false);
  Main.Score_Display.Visible:=false;
  target_theta:=2*pi;
  target_freq:=0;
  next_phase_time:=100;
  score_count:=0;current_score:=0;norm_score:=0;total_score:=0;target_move:=false;
end;

procedure init_new_phase;
var s:string;
begin
  current_phase:=current_phase+1;
  if current_phase=end_phase then current_phase:=start_phase;
  phase_time:=0;
  case current_phase of
   start_phase:
    begin
      init_new_trial;
      delay_len[1]:=0;delay_len[2]:=0
    end;
   track_phase:
    begin
     target_move:=true;
     set_vfb(true,true,false);
     next_phase_time:=round(track_time*clock_freq);
    end;
   score_phase:
    begin
      set_vfb(false,false,false);
      norm_score:=round(1000*total_score/score_count);
      str(norm_score,s);
      Main.Score_Display.Caption:=' '+s;
      Main.Score_Display.Visible:=true;
      next_phase_time:=200;target_freq:=0;
      toneoff;
    end;
   rest_phase:
    begin
      Main.Score_Display.Caption:=' +';
      next_phase_time:=100;
    end;
  end;
end;


procedure begin_task;

var waserror:boolean;dir,root,ids,s:string;p:integer;Code:integer;
begin
  waserror:=false;
  if Main.Record_On.Checked then
    begin
      dir:=Main.Pathname_Edit.text;
      if not(directoryexists(dir)) then createdir(dir);
      root:=dir+'\'+Main.Filename_Edit.text;
      ids:=Main.ID_Edit.text;
      waserror:=false;
      fn_hi:=root+'hi'+'-'+ids+'.sp'+#0;
      fid_hi:=createfile(@fn_hi[1],generic_write,0,0,create_always,FILE_FLAG_OVERLAPPED,0);
      fileoffset_hi:=0;
      if fid_hi=INVALID_HANDLE_VALUE then waserror:=true;
      fn_lo:=root+'lo'+'-'+ids+'.sp'+#0;
      fid_lo:=createfile(@fn_lo[1],generic_write,0,0,create_always,FILE_FLAG_OVERLAPPED,0);
      fileoffset_lo:=0;
      if fid_lo=INVALID_HANDLE_VALUE then waserror:=true;
      curhalf_hi:=0;curhalf_lo:=0;pointer_hi:=0;pointer_lo:=0;
      if not waserror then Main.Record_Light.Brush.Color:=clLime;
    end;
  if not waserror then
    begin
      Main.Task_Panel.Visible:=true;
      Main.StartStop.Caption:='Stop';
      init_new_list;
      trial_counter:=0;
      current_phase:=0;
      init_new_phase;
      Main.Record_On.Enabled:=false;
      Main.Pathname_Edit.Enabled:=false;
      Main.Filename_Edit.Enabled:=false;
      Main.ID_Edit.Enabled:=false;
      task_on:=true;
    end;
end;

procedure end_task;
var s:string;er:longbool;status,sampsread:longint;
begin
  Main.Task_Panel.Visible:=false;
  Main.StartStop.Caption:='Start';
  Main.Record_On.Enabled:=true;
  Main.Pathname_Edit.Enabled:=true;
  Main.Filename_Edit.Enabled:=true;
  Main.ID_Edit.Enabled:=true;
   toneoff;

  if Main.Record_On.Checked then
  begin
    ov_hi.offset:=fileoffset_hi;
    ov_hi.offsethigh:=0;
    er:=writefileex(fid_hi,@buf_hi[curhalf_hi*buflen_hi div 2],(pointer_hi mod (buflen_hi div 2))*2,ov_hi,nil);
    ov_lo.offset:=fileoffset_lo;
    ov_lo.offsethigh:=0;
    er:=writefileex(fid_lo,@buf_lo[curhalf_lo*buflen_lo div 2],(pointer_lo mod (buflen_lo div 2))*2,ov_lo,nil);
    closehandle(fid_hi);
    setfileattributes(@fn_hi[1],FILE_ATTRIBUTE_READONLY);
    closehandle(fid_lo);
    setfileattributes(@fn_lo[1],FILE_ATTRIBUTE_READONLY);
    id:=id+1;
    str(id,s);
    Main.ID_Edit.Text:=s;
    Main.Record_Light.Brush.Color:=clMaroon;
  end;
  task_on:=false;
end;

procedure TMain.FormCreate(Sender: TObject);
var s:string;status,sampsread:Longint;i:integer;
begin
  Randomize;
  Task_Panel.Width:=screen_size;
  Task_Panel.Height:=screen_size;
  Task_Panel.DoubleBuffered:=true;
  Task_Panel.Left:=round(Main.Width/2-screen_size/2);
  Task_Panel.Top:=0;

  task_on:=false;
  for i:=1 to num_chan do
    ft_zero[i]:=0;
  id:=1;
  s:='ftinput';
  daqhandle:=0;
  status:=DAQmxCreateTask(PChar(s),addr(daqhandle));


  {NI device should be Dev1}

  s:='Dev1/ai0';
  status:=DAQmxCreateAIVoltageChan(daqhandle,Pchar(s),0,DAQmx_Val_InputTermCfg_Diff,-10,10,DAQmx_Val_UnitsPreScaled_Volts,0);
  status:=DAQmxCfgSampClkTiming(daqhandle,0,5000,DAQmx_Val_Rising,DAQmx_Val_AcquisitionType_ContSamps,0);
  status:=DAQmxSetReadOverWrite(daqhandle,DAQmx_Val_OverwriteMode1_OverwriteUnreadSamps);
  DAQmxStartTask(daqhandle);

  zeroed:=false;
  Main.Task_Timer.Enabled:=true;
  delay_pointer:=0;
  fixation.Left:=round(Task_panel.Left+screen_size/2-fixation.Width/2);
  fixation.Top:=round(Task_panel.Top+screen_size/2-fixation.Height/2);
end;

procedure TMain.StartStopClick(Sender: TObject);
begin
  if task_on then

      end_task
  else
        begin_task;



end;

procedure TMain.Zero_ButtonClick(Sender: TObject);
begin
  ft_zero[1]:=ft_val[1];
  zeroed:=true;
end;


procedure TMain.Task_TimerTimer(Sender: TObject);
var status,sampsread,nsmooth,i,j:Longint;s:string;
  er:longbool;err:cardinal;
  thishalf:integer;


begin
  status:=DAQmxReadAnalogF64(daqhandle,100,-1,DAQmx_Val_GroupByScanNumber,addr(dac_data[1,1]),dac_buf_len,addr(sampsread),0);
  status:=DAQmxReadAnalogF64(daqhandle,-1,-1,DAQmx_Val_GroupByScanNumber,addr(dac_data[101,1]),dac_buf_len,addr(sampsread),0);

  sampsread:=sampsread+100;
  if sampsread>dac_buf_len then sampsread:=dac_buf_len;
  if sampsread>smooth_const then nsmooth:=smooth_const else nsmooth:=sampsread;
  str(sampsread,s);
  Sample_Count.Caption:=s;
  if nsmooth>0 then
    for j:=1 to num_chan do
      begin
        ft_val[j]:=0;
        for i:=1 to nsmooth do
          ft_val[j]:=ft_val[j]+dac_data[sampsread+1-i,j];
        ft_val[j]:=ft_val[j]/nsmooth;
      end;
  cursor_buf[delay_pointer,1]:=(ft_val[1]-ft_zero[1])*cursor_scale-1;
 if task_on then
    begin
      if not zeroed then
        begin
          ft_zero[1]:=ft_val[1];
          zeroed:=true;
        end;
      cursor_pos[1]:=cursor_buf[(delay_pointer+delay_buf_len-round(trial_list[list_counter].delay*clock_freq)) mod delay_buf_len,1];
      if abs(cursor_pos[1])>2000 then cursor_pos[1]:=sign(cursor_pos[1])*2000;
      phase_time:=phase_time+1;
      if phase_time=next_phase_time then init_new_phase;

      if target_move then
        begin
         target_pos[1]:=trial_list[list_counter].target_amp*sin(2*pi*phase_time*trial_list[list_counter].target_freq/clock_freq);
         pert[1]:=trial_list[list_counter].cursor_amp*sin(2*pi*phase_time*trial_list[list_counter].cursor_freq/clock_freq);
         cursor_pos[1]:=cursor_pos[1]+pert[1];
         current_score:=exp(-abs(cursor_pos[1]-target_pos[1])/score_const);
         score_count:=score_count+1;
         total_score:=total_score+current_score;
        end
      else
        begin current_score:=0; target_pos[1]:=0 end;

      if Main.Cursor.Visible then
        begin
          target2_pos[1]:=target_pos[1];
          target2_pos[2]:=target_pos[2]
        end
       else
        begin
          target2_pos[1]:=1/sqrt(2);
          target2_pos[2]:=1/sqrt(2)
        end;

      Target.Top:=round(screen_size/2-target_pos[1]*radius-Target.Height/2);
      Target.Left:=round(screen_size/2-Target.Width/2);
      Target2.Top:=round(screen_size/2-target2_pos[1]*radius-Target2.Height/2);
      Target2.Left:=round(screen_size/2-Target2.Width/2);
      Target3.Top:=round(screen_size/2-target3_pos[1]*radius-Target3.Height/2);
      Target3.Left:=round(screen_size/2-Target3.Width/2);
      Cursor.Top:=round(screen_size/2-cursor_pos[1]*radius-Cursor.Height/2);
      Cursor.Left:=round(screen_size/2-Cursor.Width/2);
      Cursor2.Top:=round(screen_size/2-cursor2_pos[1]*radius-Cursor2.Height/2);
      Cursor2.Left:=round(screen_size/2-Cursor2.Width/2);
      cursor2_pos[1]:=cursor_pos[1];cursor2_pos[2]:=cursor_pos[2];

{Output data:
1 - Cursor position
2 - Target position
3 - Cursor perturbation
4 - Current trial phase
5 - Trial condition (corresponding to the list you define)
6,7,8 - Relate to calculation of score
9 - Samples read per clock cycle
}

      data_lo[1]:=round(cursor_pos[1]*500);
      data_lo[2]:=round(target_pos[1]*500);
      data_lo[3]:=round(pert[1]*500);
      data_lo[4]:=current_phase;
      data_lo[5]:=trial_list[list_counter].cond;
      data_lo[6]:=round(total_score);data_lo[7]:=score_count;
      data_lo[8]:=round(current_score*1000);data_lo[9]:=sampsread;
      if Main.Record_On.Checked then
        begin
          for i:=1 to num_lo do
            buf_lo[pointer_lo+i-1]:=data_lo[i];
          pointer_lo:=(pointer_lo+num_lo) mod buflen_lo;
          thishalf:=pointer_lo div (buflen_lo div 2);
          if thishalf<>curhalf_lo then
            begin
              ov_lo.offset:=fileoffset_lo;
              ov_lo.offsethigh:=0;
              fileoffset_lo:=fileoffset_lo+buflen_lo;
              er:=writefileex(fid_lo,@buf_lo[curhalf_lo*buflen_lo div 2],buflen_lo,ov_lo,nil);
              if longint(er)=0 then Record_Light.Brush.Color:=clRed;
              curhalf_lo:=1-curhalf_lo;
            end;
          for i:=1 to sampsread do
            begin
              for j:=1 to num_chan do
                buf_hi[pointer_hi+j-1]:=round(1000*dac_data[i,j]);
              pointer_hi:=(pointer_hi+num_chan) mod buflen_hi
            end;
          thishalf:=pointer_hi div (buflen_hi div 2);
          if thishalf<>curhalf_hi then
            begin
              ov_hi.offset:=fileoffset_hi;
              ov_hi.offsethigh:=0;
              fileoffset_hi:=fileoffset_hi+buflen_hi;
              er:=writefileex(fid_hi,@buf_hi[curhalf_hi*buflen_hi div 2],buflen_hi,ov_hi,nil);
              if longint(er)=0 then Record_Light.Brush.Color:=clRed;
              curhalf_hi:=1-curhalf_hi;
            end;
        end;
    end;
    delay_pointer:=(delay_pointer+1) mod delay_buf_len;
end;



procedure TMain.ID_EditChange(Sender: TObject);
var Code,oldid:integer;ids:string;
begin
   oldid:=id;
   val(ID_Edit.Text,id,Code);
   if Code>0 then
     begin
       id:=oldid;
       str(id,ids);
       ID_Edit.Text:=ids
     end
end;

procedure TMain.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  if task_on then end_task;
  DAQmxStopTask(daqhandle);
  DAQmxStopTask(dighandle);
  DAQmxStopTask(dighandle2);

end;

end.
