import React from 'react';
import {Composition} from 'remotion';
import {Recurso, defaultProps} from './Plantillas';

// Una sola composición: la plantilla va en las props (precapcut.py las pasa con --props).
export const Root: React.FC = () => (
	<Composition
		id="Recurso"
		component={Recurso}
		width={1080}
		height={1920}
		fps={30}
		durationInFrames={60}
		defaultProps={defaultProps}
		calculateMetadata={({props}) => ({durationInFrames: Math.max(15, Math.round(props.duracion * 30))})}
	/>
);
