unit usetone;

interface

procedure starttone(f,warble:single);
procedure toneoff;

var       istone:boolean;

implementation
uses mmsystem;
var   hwaveout:integer;
      wavehdr:twavehdr;
      buf:array[0..7999] of smallint;
      waveformatex:twaveformatex;

procedure starttone(f,warble:single);
var n,e,w:integer;
begin
if f=0 then begin
            toneoff;
            exit;
            end;
if istone then toneoff;
if warble=0 then w:=50000
            else w:=round(warble*8000/2);
for n:=0 to 7999 do
   begin
   if ((n div w) mod 2)=0 then buf[n]:=round(15000*sin (2*3.14159*f*n/8000))
                          else buf[n]:=0;
   end;
with wavehdr do
  begin
  lpdata:=@buf;
  dwbufferlength:=16000;
  dwflags:=whdr_beginloop or whdr_endloop;
  dwloops:=100;
  end;
waveoutprepareheader (hwaveout,@wavehdr,sizeof (wavehdr));
waveoutwrite (hwaveout,@wavehdr,sizeof (wavehdr));
istone:=true;
end;

procedure toneoff;
begin
waveoutreset (hwaveout);
waveoutunprepareheader (hwaveout,@wavehdr,sizeof(wavehdr));
istone:=false;
end;

begin
with waveformatex do
 begin
 wformattag:=wave_format_pcm;
 nchannels:=1;
 nsamplespersec:=8000;
 nAvgBytesPerSec:=16000;
 nblockalign:=2;
 wBitsPerSample:=16;
 cbsize:=0;
 end;
waveoutopen (@hwaveout,wave_mapper,@waveformatex,0,0,callback_null);

end.
 