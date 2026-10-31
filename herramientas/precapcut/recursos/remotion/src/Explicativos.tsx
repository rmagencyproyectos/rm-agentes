import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Props} from './Plantillas';

// Ilustraciones que EXPLICAN lo que se dice (Gerard 31/10: nada de iconos de relleno).
// Línea plana en el color de la marca + blanco, sobre tarjeta oscura translúcida. t1/t2: segundos
// (desde que entra el recurso) en que pasa cada cosa, sincronizados con la palabra.
const ROJO = '#c8463c';

const Tarjeta: React.FC<{p: Props; titulo: string; children: React.ReactNode}> = ({p, titulo, children}) => (
	<div style={{width: 680, padding: '28px 34px 22px', borderRadius: 44, background: 'rgba(22,16,12,0.62)',
		boxShadow: '0 20px 50px rgba(0,0,0,0.35)', display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
		<svg width={612} height={300} viewBox="0 0 612 300">{children}</svg>
		<div style={{fontFamily: 'Texto', fontSize: 46, color: '#fff', marginTop: 10}}>{titulo}</div>
	</div>
);

const useT = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	return {s: f / fps, f, fps};
};
const paso = (s: number, a: number, dur = 0.35) => interpolate(s, [a, a + dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

// 1) Cajón visto desde arriba: bandeja estándar de plástico con huecos -> madera a medida que se estira.
export const Cajon: React.FC<{p: Props}> = ({p}) => {
	const {s} = useT();
	const madera = paso(s, p.t1);
	const estira = paso(s, p.t2, 0.6);
	const ancho = interpolate(estira, [0, 1], [380, 532]);
	const x = 306 - ancho / 2;
	const huecos = 1 - estira;
	const parpadeo = 0.55 + 0.45 * Math.sin(s * 10);
	const color = madera > 0.5 ? p.color : '#9aa0a6';
	const titulo = estira > 0.5 ? 'a medida del cajón' : madera > 0.5 ? 'de madera' : 'medida estándar';
	return (
		<Tarjeta p={p} titulo={titulo}>
			<rect x={30} y={30} width={552} height={240} rx={14} fill="none" stroke="#fff" strokeWidth={6} />
			{huecos > 0.02 && [40, 306 + ancho / 2].map((hx) => (
				<rect key={hx} x={hx} y={40} width={(532 - ancho) / 2} height={220} fill={ROJO} opacity={huecos * parpadeo * 0.85} />
			))}
			<rect x={x} y={40} width={ancho} height={220} rx={10} fill={color} />
			{[1, 2, 3].map((i) => <line key={i} x1={x + (ancho * i) / 4} y1={50} x2={x + (ancho * i) / 4} y2={250} stroke="rgba(255,255,255,0.55)" strokeWidth={5} />)}
			{madera > 0.5 && [0, 1, 2, 3, 4].map((i) => <path key={i} d={`M${x + 8} ${70 + i * 40} q ${ancho / 4} -8 ${ancho - 16} 0`} stroke="rgba(0,0,0,0.12)" strokeWidth={3} fill="none" />)}
			{huecos > 0.5 && <text x={306} y={292} fill={ROJO} fontFamily="Texto" fontSize={26} textAnchor="middle" opacity={huecos}>hueco perdido</text>}
		</Tarjeta>
	);
};

// 2) El mismo cajón de madera: los compartimentos se llenan de cubiertos ordenados y sale un check.
const Tenedor = ({x}: {x: number}) => <path d={`M${x - 14} 70 v40 M${x} 70 v40 M${x + 14} 70 v40 M${x - 14} 110 q14 22 28 0 M${x} 128 v110`} stroke="#fff" strokeWidth={6} fill="none" strokeLinecap="round" />;
const Cuchillo = ({x}: {x: number}) => <path d={`M${x} 70 q16 40 0 90 v78`} stroke="#fff" strokeWidth={7} fill="none" strokeLinecap="round" />;
const Cuchara = ({x}: {x: number}) => <g><ellipse cx={x} cy={95} rx={16} ry={24} fill="none" stroke="#fff" strokeWidth={6} /><path d={`M${x} 119 v119`} stroke="#fff" strokeWidth={6} strokeLinecap="round" /></g>;
export const CajonOrden: React.FC<{p: Props}> = ({p}) => {
	const {f, fps, s} = useT();
	const piezas = [Tenedor, Cuchillo, Cuchara, Tenedor];
	return (
		<Tarjeta p={p} titulo="todo organizado">
			<rect x={30} y={30} width={552} height={240} rx={14} fill={p.color} stroke="#fff" strokeWidth={6} />
			{[1, 2, 3].map((i) => <line key={i} x1={30 + 138 * i} y1={40} x2={30 + 138 * i} y2={260} stroke="rgba(255,255,255,0.55)" strokeWidth={5} />)}
			{piezas.map((P, i) => {
				const v = spring({frame: f - (0.25 + i * 0.3) * fps, fps, config: {damping: 13}});
				return <g key={i} opacity={v} transform={`translate(0 ${(1 - v) * -40})`}><P x={99 + 138 * i} /></g>;
			})}
			<path d="M500 230 l22 22 l44 -50" stroke="#7fd18b" strokeWidth={12} fill="none" strokeLinecap="round" strokeLinejoin="round"
				pathLength={1} strokeDasharray={1} strokeDashoffset={1 - paso(s, 1.6, 0.4)} />
		</Tarjeta>
	);
};

// 3 y 4) Planta de una cocina en L vista desde arriba: la esquina es espacio muerto; el riñonero
// saca dos bandejas en forma de riñón girando y la esquina pasa a aprovecharse.
const PlantaL: React.FC<{p: Props; rincon: number; aprovechado: number}> = ({p, rincon, aprovechado}) => (
	<g>
		<path d="M60 40 H560 V150 H170 V280 H60 Z" fill="none" stroke="#fff" strokeWidth={6} strokeLinejoin="round" />
		{[270, 360, 450].map((x) => <line key={x} x1={x} y1={40} x2={x} y2={150} stroke="rgba(255,255,255,0.5)" strokeWidth={4} />)}
		<line x1={170} y1={40} x2={170} y2={150} stroke="rgba(255,255,255,0.5)" strokeWidth={4} />
		<line x1={60} y1={150} x2={170} y2={150} stroke="rgba(255,255,255,0.5)" strokeWidth={4} />
		<defs>
			<pattern id="rayas" width={14} height={14} patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
				<rect width={7} height={14} fill={aprovechado > 0.5 ? p.color : ROJO} />
			</pattern>
		</defs>
		{/* la esquina donde se juntan los dos brazos de la L: ahí no llega la mano */}
		<rect x={66} y={46} width={98} height={98} fill="url(#rayas)" opacity={rincon} />
		<rect x={66} y={46} width={98} height={98} fill="none" stroke={aprovechado > 0.5 ? p.color : ROJO} strokeWidth={5} opacity={Math.min(1, rincon * 1.5)} />
	</g>
);
export const Esquina: React.FC<{p: Props}> = ({p}) => {
	const {s} = useT();
	const late = 0.75 + 0.25 * Math.sin(s * 6);
	return (
		<Tarjeta p={p} titulo="rincón perdido">
			<PlantaL p={p} rincon={paso(s, 0.5) * late} aprovechado={0} />
			<path d="M300 250 C 260 230 220 200 175 160" stroke={ROJO} strokeWidth={6} fill="none" strokeDasharray="10 10" opacity={paso(s, 0.8)} />
		</Tarjeta>
	);
};
const Rinon: React.FC<{giro: number; dy: number; color: string}> = ({giro, dy, color}) => (
	<g transform={`translate(${70 + dy} 52) rotate(${giro})`}>
		<path d="M0 0 C 80 -10 150 20 150 70 C 150 110 110 120 80 100 C 60 88 30 100 10 110 C -10 80 -10 30 0 0 Z" fill={color} stroke="#fff" strokeWidth={4} />
	</g>
);
export const Rinonero: React.FC<{p: Props}> = ({p}) => {
	const {s} = useT();
	const sale = paso(s, 0.4, 0.9);
	const usa = paso(s, p.t1, 0.5);
	return (
		<Tarjeta p={p} titulo={usa > 0.5 ? 'todo el hueco aprovechado' : 'riñonero'}>
			<PlantaL p={p} rincon={0.35 + 0.65 * usa} aprovechado={usa} />
			<Rinon giro={interpolate(sale, [0, 1], [0, 38])} dy={10} color="#b7b9bc" />
			<Rinon giro={interpolate(sale, [0, 1], [0, 62])} dy={70} color="#a3a6aa" />
		</Tarjeta>
	);
};

// 5) CTA: botón de guardar de Instagram (dibujado) que se rellena.
export const Guardar: React.FC<{p: Props}> = ({p}) => {
	const {f, fps, s} = useT();
	const lleno = paso(s, 0.45, 0.25);
	const bote = 1 + 0.18 * spring({frame: f - 0.45 * fps, fps, config: {damping: 8}}) * (1 - paso(s, 0.9, 0.4));
	return (
		<Tarjeta p={p} titulo="Guárdalo">
			<g transform={`translate(306 150) scale(${bote}) translate(-306 -150)`}>
				<path d="M246 40 H366 Q378 40 378 52 V262 L306 214 L234 262 V52 Q234 40 246 40 Z" fill={lleno > 0.5 ? '#fff' : 'none'} stroke="#fff" strokeWidth={14} strokeLinejoin="round" />
			</g>
		</Tarjeta>
	);
};
