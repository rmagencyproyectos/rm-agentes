// Convierte cualquier audio que sepa leer AVFoundation (incluido el Ogg-Opus de
// WhatsApp) a WAV mono 16 kHz, que es lo que come Whisper. Evita depender de
// ffmpeg, que no está instalado.
// Uso: swift opus2wav.swift entrada.opus salida.wav
import AVFoundation

let entrada = URL(fileURLWithPath: CommandLine.arguments[1])
let salida = URL(fileURLWithPath: CommandLine.arguments[2])

// Todo dentro de una función a propósito: AVAudioFile solo cierra la cabecera
// del WAV cuando se libera. Si el objeto vive hasta el final del proceso, el
// fichero queda con tamaño de datos 0 y quien lo lea ve un audio vacío.
func convertir() throws -> Int64 {
    let origen = try AVAudioFile(forReading: entrada)
    let destinoFmt = AVAudioFormat(commonFormat: .pcmFormatInt16, sampleRate: 16000,
                                   channels: 1, interleaved: true)!
    let destino = try AVAudioFile(forWriting: salida, settings: destinoFmt.settings,
                                  commonFormat: .pcmFormatInt16, interleaved: true)
    let conv = AVAudioConverter(from: origen.processingFormat, to: destinoFmt)!
    let bufIn = AVAudioPCMBuffer(pcmFormat: origen.processingFormat, frameCapacity: 32768)!

    while true {
        let bufOut = AVAudioPCMBuffer(pcmFormat: destinoFmt, frameCapacity: 32768)!
        var err: NSError?
        let estado = conv.convert(to: bufOut, error: &err) { _, sinPtr in
            do {
                try origen.read(into: bufIn)
            } catch { sinPtr.pointee = .endOfStream; return nil }
            if bufIn.frameLength == 0 { sinPtr.pointee = .endOfStream; return nil }
            sinPtr.pointee = .haveData
            return bufIn
        }
        if let err = err { throw err }
        if bufOut.frameLength > 0 { try destino.write(from: bufOut) }
        if estado == .endOfStream || estado == .error { break }
    }
    return destino.length
}

let frames = try convertir()
print("ok \(salida.lastPathComponent) — \(frames / 16000) s")
