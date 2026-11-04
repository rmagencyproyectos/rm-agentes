import React from 'react';
import {CameraMotionBlur} from '@remotion/motion-blur';
import {AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {AntesDespues, Cajon, CajonOrden, ColorCansa, Esquina, Guardar, MovilFoto, Muestrario, Puzle, Rayado, Rinonero, Rotulo} from './Explicativos';
import {ColorCansa3D, MovilFoto3D, Muestrario3D, Puzle3D, Rayado3D} from './Explicativos3D';

// Plantillas de motion graphics de precapcut. Fondo transparente; el elemento va centrado en (x, y)
// en píxeles de 1080x1920. Colores y fuentes llegan del estilo del cliente.
export type Props = {
	plantilla: 'carpeta' | 'icono' | 'contador' | 'check' | 'cruz' | 'lista' | 'flecha' | 'cajon' | 'cajon_orden' | 'esquina' | 'rinonero' | 'guardar' | 'antes_despues' | 'etiqueta' | 'rayado' | 'color_cansa' | 'puzle' | 'muestrario' | 'movil_foto' | 'rayado_3d' | 'color_cansa_3d' | 'puzle_3d' | 'muestrario_3d' | 'movil_foto_3d';
	t1: number;
	t2: number;
	texto: string;
	icono: string;
	items: string[];
	numero: number;
	duracion: number;
	x: number;
	y: number;
	color: string;
	colorTexto: string;
	fuenteTitulo: string;
	fuenteTexto: string;
	desenfoque: boolean; // motion blur: solo en el render final (en Studio va lento)
};

export const defaultProps: Props = {
	plantilla: 'icono', texto: 'riñonero', icono: '🗄️', items: [], numero: 3, duracion: 2,
	t1: 1, t2: 2, x: 540, y: 1350, color: '#985e34', colorTexto: '#ffffff', fuenteTitulo: 'Rubik-Bold.ttf', fuenteTexto: 'Alata-Regular.ttf', desenfoque: false,
};

const fuentes = (p: Props) => `
@font-face {font-family: Titulo; src: url(${staticFile(p.fuenteTitulo)});}
@font-face {font-family: Texto; src: url(${staticFile(p.fuenteTexto)});}`;

// Entrada con muelle que llega enfocándose (blur → nítido), respiración suave y salida que se desenfoca.
const SALIDA = 9;
const useAnim = () => {
	const f = useCurrentFrame();
	const {fps, durationInFrames} = useVideoConfig();
	const entra = spring({frame: f, fps, config: {damping: 14, stiffness: 140}});
	const sale = interpolate(f, [durationInFrames - SALIDA, durationInFrames - 1], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const respira = 1 + 0.015 * Math.sin(f / 8);
	const blur = Math.max(0, 1 - entra) * 18 + (1 - sale) * 14;
	return {f, fps, escala: (0.85 + 0.15 * entra) * (0.92 + 0.08 * sale) * respira, opacidad: Math.min(1, entra * 1.6) * sale, blur};
};

const Etiqueta: React.FC<{p: Props; texto: string; tam?: number}> = ({p, texto, tam = 54}) => (
	<div style={{fontFamily: 'Texto', fontSize: tam, color: p.colorTexto, textShadow: '0 4px 14px rgba(0,0,0,0.45)', marginTop: 18, textAlign: 'center'}}>
		{texto}
	</div>
);

const Carpeta: React.FC<{p: Props}> = ({p}) => (
	<div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
		<svg width={300} height={240} viewBox="0 0 300 240">
			<path d="M20 40 Q20 20 40 20 H120 L145 45 H260 Q280 45 280 65 V200 Q280 220 260 220 H40 Q20 220 20 200 Z" fill={p.color} />
			<path d="M20 80 Q20 65 35 65 H265 Q280 65 280 80 V200 Q280 220 260 220 H40 Q20 220 20 200 Z" fill={p.color} style={{filter: 'brightness(1.25)'}} />
		</svg>
		<Etiqueta p={p} texto={p.texto} />
	</div>
);

const Icono: React.FC<{p: Props}> = ({p}) => (
	<div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
		<div style={{width: 260, height: 260, borderRadius: 64, background: p.color, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 18px 40px rgba(0,0,0,0.35)'}}>
			<span style={{fontSize: 150}}>{p.icono}</span>
		</div>
		<Etiqueta p={p} texto={p.texto} />
	</div>
);

const Contador: React.FC<{p: Props; f: number; fps: number}> = ({p, f, fps}) => {
	const n = Math.round(interpolate(f, [0, fps * 0.8], [0, p.numero], {extrapolateRight: 'clamp'}));
	return (
		<div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
			<div style={{fontFamily: 'Titulo', fontSize: 260, color: p.color, lineHeight: 1, textShadow: '0 10px 30px rgba(0,0,0,0.35)'}}>{n}</div>
			<Etiqueta p={p} texto={p.texto} />
		</div>
	);
};

const Marca: React.FC<{p: Props; ok: boolean; f: number}> = ({p, ok, f}) => {
	const trazo = interpolate(f, [3, 14], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return (
		<div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
			<svg width={260} height={260} viewBox="0 0 100 100">
				<circle cx={50} cy={50} r={46} fill={ok ? '#3c8d4f' : '#b8352f'} />
				<path d={ok ? 'M28 52 L44 67 L73 35' : 'M32 32 L68 68 M68 32 L32 68'} stroke="#fff" strokeWidth={9} strokeLinecap="round" fill="none"
					pathLength={1} strokeDasharray={1} strokeDashoffset={trazo} />
			</svg>
			<Etiqueta p={p} texto={p.texto} />
		</div>
	);
};

const Lista: React.FC<{p: Props; f: number; fps: number}> = ({p, f, fps}) => (
	<div style={{display: 'flex', flexDirection: 'column', gap: 18, alignItems: 'flex-start'}}>
		{p.items.map((it, i) => {
			const v = spring({frame: f - i * fps * 0.35, fps, config: {damping: 14}});
			return (
				<div key={it} style={{opacity: v, transform: `translateX(${(1 - v) * -60}px)`, display: 'flex', alignItems: 'center', gap: 20,
					background: p.color, borderRadius: 28, padding: '14px 30px', fontFamily: 'Texto', fontSize: 50, color: p.colorTexto}}>
					<span>✓</span>{it}
				</div>
			);
		})}
	</div>
);

const Flecha: React.FC<{p: Props; f: number}> = ({p, f}) => (
	<div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
		<Etiqueta p={p} texto={p.texto} />
		<svg width={200} height={220} viewBox="0 0 100 110" style={{transform: `translateY(${Math.sin(f / 5) * 10}px)`}}>
			<path d="M50 5 V85 M20 60 L50 92 L80 60" stroke={p.color} strokeWidth={12} strokeLinecap="round" strokeLinejoin="round" fill="none" />
		</svg>
	</div>
);

export const Recurso: React.FC<Props> = (p) => {
	const {f, fps, escala, opacidad, blur} = useAnim();
	const cuerpo = {
		carpeta: <Carpeta p={p} />,
		icono: <Icono p={p} />,
		contador: <Contador p={p} f={f} fps={fps} />,
		check: <Marca p={p} ok f={f} />,
		cruz: <Marca p={p} ok={false} f={f} />,
		lista: <Lista p={p} f={f} fps={fps} />,
		flecha: <Flecha p={p} f={f} />,
		cajon: <Cajon p={p} />,
		cajon_orden: <CajonOrden p={p} />,
		esquina: <Esquina p={p} />,
		rinonero: <Rinonero p={p} />,
		guardar: <Guardar p={p} />,
		antes_despues: <AntesDespues p={p} />,
		etiqueta: <Rotulo p={p} />,
		rayado: <Rayado p={p} />,
		color_cansa: <ColorCansa p={p} />,
		puzle: <Puzle p={p} />,
		muestrario: <Muestrario p={p} />,
		movil_foto: <MovilFoto p={p} />,
		rayado_3d: <Rayado3D p={p} />,
		color_cansa_3d: <ColorCansa3D p={p} />,
		puzle_3d: <Puzle3D p={p} />,
		muestrario_3d: <Muestrario3D p={p} />,
		movil_foto_3d: <MovilFoto3D p={p} />,
	}[p.plantilla];
	const capa = (
		<AbsoluteFill style={{backgroundColor: 'transparent'}}>
			<style>{fuentes(p)}</style>
			<div style={{position: 'absolute', left: p.plantilla.endsWith('_3d') ? Math.min(Math.max(p.x, 270), 810) : p.x, top: p.y, transform: `translate(-50%, -50%) scale(${escala})`, opacity: opacidad,
				filter: blur > 0.05 ? `blur(${blur}px)` : undefined}}>
				{cuerpo}
			</div>
		</AbsoluteFill>
	);
	return p.desenfoque ? <CameraMotionBlur shutterAngle={180} samples={8}>{capa}</CameraMotionBlur> : capa;
};
