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

// Antes / después en dos mitades, de golpe (Gerard 31/10: ~2 s, concreto; elegido «B»).
const Bandeja: React.FC<{x: number; ancho: number; color: string; huecos: boolean; parpadeo: number}> = ({x, ancho, color, huecos, parpadeo}) => (
	<g>
		<rect x={x} y={40} width={250} height={190} rx={12} fill="none" stroke="#fff" strokeWidth={5} />
		{huecos && [x + 6, x + 125 + ancho / 2].map((hx) => (
			<rect key={hx} x={hx} y={46} width={(238 - ancho) / 2} height={178} fill={ROJO} opacity={0.5 + 0.4 * parpadeo} />
		))}
		<rect x={x + 125 - ancho / 2} y={46} width={ancho} height={178} rx={8} fill={color} />
		{[1, 2, 3].map((i) => <line key={i} x1={x + 125 - ancho / 2 + (ancho * i) / 4} y1={54} x2={x + 125 - ancho / 2 + (ancho * i) / 4} y2={216} stroke="rgba(255,255,255,0.55)" strokeWidth={4} />)}
	</g>
);
export const AntesDespues: React.FC<{p: Props}> = ({p}) => {
	const {s} = useT();
	const parpadeo = Math.sin(s * 10);
	const derecha = paso(s, p.t1, 0.2);
	return (
		<div style={{width: 680, padding: '26px 30px 20px', borderRadius: 44, background: 'rgba(22,16,12,0.62)', boxShadow: '0 20px 50px rgba(0,0,0,0.35)'}}>
			<svg width={620} height={250} viewBox="0 0 620 250">
				<Bandeja x={20} ancho={170} color="#9aa0a6" huecos parpadeo={parpadeo} />
				<line x1={310} y1={30} x2={310} y2={240} stroke="rgba(255,255,255,0.35)" strokeWidth={3} />
				<g opacity={derecha} transform={`translate(${(1 - derecha) * 20} 0)`}>
					<Bandeja x={350} ancho={238} color={p.color} huecos={false} parpadeo={0} />
				</g>
			</svg>
			{/* sin texto (Gerard 31/10: el texto ya va en los titulares): la imagen se explica sola */}
			<svg width={620} height={90} viewBox="0 0 620 90">
				<g transform="translate(145 45)"><circle r={36} fill={ROJO} /><path d="M-15 -15 L15 15 M15 -15 L-15 15" stroke="#fff" strokeWidth={8} strokeLinecap="round" /></g>
				<g transform="translate(475 45)" opacity={derecha}><circle r={36} fill="#3c8d4f" /><path d="M-17 1 L-5 14 L18 -12" stroke="#fff" strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" fill="none" /></g>
			</svg>
		</div>
	);
};

// Rótulo sobre el objeto real («riñonero = rincón aprovechado»): la palabra en grande y la explicación.
export const Rotulo: React.FC<{p: Props}> = ({p}) => {
	const [clave, ...resto] = p.texto.split('=');
	return (
		<div style={{padding: '22px 40px', borderRadius: 40, background: 'rgba(22,16,12,0.62)', textAlign: 'center', boxShadow: '0 20px 50px rgba(0,0,0,0.35)'}}>
			<div style={{fontFamily: 'Titulo', fontSize: 92, color: p.color, lineHeight: 1}}>{clave.trim().toUpperCase()}</div>
			{resto.length > 0 && <div style={{fontFamily: 'Texto', fontSize: 46, color: '#fff', marginTop: 8}}>= {resto.join('=').trim()}</div>}
		</div>
	);
};

// ---- Recursos sin texto (Gerard 31/10 y 03/11): dibujo reconocible + animación, ~2 s, pequeño en una esquina.
const Mini: React.FC<{children: React.ReactNode}> = ({children}) => (
	<div style={{width: 400, height: 300, borderRadius: 36, background: 'rgba(22,16,12,0.55)', boxShadow: '0 16px 40px rgba(0,0,0,0.35)',
		display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
		<svg width={360} height={260} viewBox="0 0 360 260">{children}</svg>
	</div>
);

// «materiales delicados»: encimera brillante, pasa un reflejo y se dibuja una raya con grieta.
export const Rayado: React.FC<{p: Props}> = ({p}) => {
	const {s} = useT();
	const reflejo = interpolate(s, [0, 0.9], [-120, 380], {extrapolateRight: 'clamp'});
	const raya = paso(s, 0.55, 0.2);
	return (
		<Mini>
			<defs><clipPath id="enc"><rect x={30} y={70} width={300} height={130} rx={12} /></clipPath></defs>
			<rect x={30} y={70} width={300} height={130} rx={12} fill="#f1ede6" />
			<g clipPath="url(#enc)"><rect x={reflejo} y={40} width={60} height={200} fill="#fff" opacity={0.7} transform={`skewX(-20)`} /></g>
			<rect x={30} y={70} width={300} height={130} rx={12} fill="none" stroke="#c9c2b8" strokeWidth={4} />
			<path d="M70 110 L150 140 L210 128 L290 170" stroke={ROJO} strokeWidth={6} fill="none" strokeLinecap="round"
				pathLength={1} strokeDasharray={1} strokeDashoffset={1 - raya} />
			<path d="M150 140 l-10 22 M210 128 l14 -20" stroke={ROJO} strokeWidth={4} fill="none" strokeLinecap="round" opacity={paso(s, 0.75, 0.15)} />
		</Mini>
	);
};

// «colores que cansan»: muestra muy viva que se apaga a gris.
export const ColorCansa: React.FC<{p: Props}> = () => {
	const {s} = useT();
	const k = paso(s, 0.25, 0.6);
	const mezcla = (a: number[], b: number[]) => `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * k)).join(',')})`;
	return (
		<Mini>
			{[[255, 112, 40], [0, 196, 180], [255, 214, 0]].map((c, i) => (
				<rect key={i} x={45 + i * 95} y={60 + Math.sin(s * 3 + i) * 4} width={80} height={140} rx={14}
					fill={mezcla(c, [128, 128, 126])} transform={`rotate(${(i - 1) * 6} ${85 + i * 95} 130)`} />
			))}
		</Mini>
	);
};

// «no encajan con el resto de la casa»: pieza de puzle que intenta entrar en la casa y rebota.
export const Puzle: React.FC<{p: Props}> = ({p}) => {
	const {s} = useT();
	const ida = interpolate(s, [0.1, 0.55, 0.75, 1.1], [150, 0, 26, 18], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const giro = interpolate(s, [0.55, 0.75], [0, 14], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const pieza = 'M0 0 h22 a12 12 0 1 1 24 0 h22 v22 a12 12 0 1 0 0 24 v22 h-68 Z';
	return (
		<Mini>
			<path d="M40 120 L130 50 L220 120 V220 H40 Z" fill="none" stroke="#fff" strokeWidth={7} strokeLinejoin="round" />
			<path d="M96 150 h22 a12 12 0 1 0 24 0 h22 v70 h-68 Z" fill="rgba(255,255,255,0.15)" stroke="#fff" strokeWidth={3} strokeDasharray="8 6" />
			<g transform={`translate(${190 + ida} 130) rotate(${giro})`}><path d={pieza} fill={ROJO} stroke="#fff" strokeWidth={3} /></g>
		</Mini>
	);
};

// «comparar texturas, colores y acabados»: muestrario que se abre en abanico (madera, mármol, lacado).
export const Muestrario: React.FC<{p: Props}> = ({p}) => {
	const {f, fps} = useT();
	const muestras = [
		{fill: '#8a5a33', vetas: 'rgba(60,35,15,0.5)'},
		{fill: '#e9e6e1', vetas: 'rgba(120,120,125,0.55)'},
		{fill: p.color, vetas: 'rgba(0,0,0,0)'},
	];
	return (
		<Mini>
			{muestras.map((m, i) => {
				const v = spring({frame: f - (p.t1 || 0.2) * fps * 0 - i * 0.35 * fps, fps, config: {damping: 12}});
				return (
					<g key={i} transform={`rotate(${(i - 1) * 22 * v} 180 230)`}>
						<rect x={130} y={40} width={100} height={190} rx={12} fill={m.fill} stroke="#fff" strokeWidth={3} />
						{[0, 1, 2, 3].map((k) => <path key={k} d={`M${140 + k * 22} 50 q 10 80 -4 170`} stroke={m.vetas} strokeWidth={4} fill="none" />)}
					</g>
				);
			})}
		</Mini>
	);
};

// «verlo en una foto que verlo delante tuyo»: móvil con la foto plana; la cocina sale de la pantalla con volumen.
export const MovilFoto: React.FC<{p: Props}> = ({p}) => {
	const {f, fps} = useT();
	const sale = spring({frame: f - 0.6 * fps, fps, config: {damping: 13}});
	const cocina = (esc: number, dy: number, sombra: boolean) => (
		<g transform={`translate(180 ${130 + dy}) scale(${esc}) translate(-60 -40)`}>
			{sombra && <ellipse cx={60} cy={92} rx={70} ry={8} fill="rgba(0,0,0,0.35)" />}
			<rect x={0} y={0} width={120} height={36} rx={4} fill="#f2f2f0" />
			<rect x={0} y={44} width={120} height={44} rx={4} fill={p.color} />
			{[30, 60, 90].map((x) => <line key={x} x1={x} y1={44} x2={x} y2={88} stroke="#fff" strokeWidth={2} />)}
		</g>
	);
	return (
		<Mini>
			<rect x={125} y={20} width={110} height={220} rx={18} fill="#1d1d1f" stroke="#fff" strokeWidth={4} />
			<g opacity={1 - sale}>{cocina(0.75, -10, false)}</g>
			<g opacity={sale}>{cocina(0.75 + 0.75 * sale, -10 - 10 * sale, true)}</g>
		</Mini>
	);
};
