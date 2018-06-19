(* ::Package:: *)

p=Part[Import["vol.txt", "Table"],All,1];
n=Length[p];
timescale = 0.025;
time = timescale*n;
pitch=Table[{time*r,p[[((n-1)*r)+1]]},{r,0,1,2/(n-1)}];

v[A_,t0_,t1_,t_]:=If[(t<t0||t1<t),0,A*((30*((t-t0)^4)/((t1-t0)^5))-(60*((t-t0)^3)/((t1-t0)^4))+(30*((t-t0)^2)/((t1-t0)^3)))];
velocity[A1_,T1_,A2_,T2_,A3_,t_]:=v[A1,0,T1,t]+v[A2,time-T2,time,t]+v[A3,0,time,t];

diff[A1_,T1_,A2_,T2_,A3_,pair_]:=(pair[[2]]-velocity[A1,T1,A2,T2,A3,pair[[1]]])^2;
error[A1_,T1_,A2_,T2_,A3_]:=Total[Map[Function[p,diff[A1,T1,A2,T2,A3,p]],pitch]];

result=NMinimize[{error[a1,t1,a2,t2,a3],a1>0,a2>0,a3>0,0<t1,t1<time,0<t2,t2<time},{a1,t1,a2,t2,a3}];
params=Values[Part[result,2]];
A1=Part[params,1];
T1=Part[params,2];
A2=Part[params,3];
T2=Part[params,4];
A3=Part[params,5];

timedatas={};
amp = {};
AppendTo[timedatas,time];
AppendTo[timedatas,T1];
AppendTo[timedatas,T2];
AppendTo[amp,A1];
AppendTo[amp,A2];
AppendTo[amp,A3];

Export["timedatas.txt",timedatas,"List"];
Export["amplitudes.txt",amp,"List"];
Export["opt_pitch.jpg",Plot[{velocity[A1,T1,A2,A3,T2,t],Interpolation[pitch,InterpolationOrder->4][t]},{t,0,time},PlotRange->All]];
