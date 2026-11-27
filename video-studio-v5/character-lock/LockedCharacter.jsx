import React from "react";
import {useCurrentFrame,useVideoConfig} from "remotion";
import {CHARACTER_ID,characterSVG} from "./STICKMAN_001.mjs";
// Frame-deterministic locked 2D overlay. Environment must be composed below it.
// This is an integration component, not a standalone composition.
export function LockedCharacter({motion="idle",expression="happy",left=0,top=0,width=290,height=415}){
 const frame=useCurrentFrame(),{fps}=useVideoConfig();
 const svg=characterSVG({id:CHARACTER_ID,frame,fps,motion,expression});
 return <img alt={CHARACTER_ID} src={"data:image/svg+xml;charset=utf-8,"+encodeURIComponent(svg)} style={{position:"absolute",left,top,width,height,objectFit:"contain",pointerEvents:"none"}}/>;
}
