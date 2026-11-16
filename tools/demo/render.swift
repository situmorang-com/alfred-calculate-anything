// Draws each frame of the README animation's storyboard as a PNG, styled after Alfred's
// "Experimental Big Sur Dark" theme on a gradient, and writes frames.ffconcat for ffmpeg.
//
//   swiftc -O -o render tools/demo/render.swift && ./render board.json <output folder>
import AppKit
import CoreImage

struct Row: Decodable { let title: String; let subtitle: String; let icon: String }
struct Frame: Decodable {
    let query: String; let rows: [Row]; let caption: String; let duration: Double
    let selectAll: Bool; let cursor: Bool
}
struct Board: Decodable { let width: Double; let height: Double; let scale: Double; let frames: [Frame] }

let arguments = CommandLine.arguments
guard arguments.count == 3 else {
    FileHandle.standardError.write("usage: render board.json <output folder>\n".data(using: .utf8)!)
    exit(2)
}
let board = try! JSONDecoder().decode(Board.self, from: Data(contentsOf: URL(fileURLWithPath: arguments[1])))
let output = URL(fileURLWithPath: arguments[2], isDirectory: true)

let W = CGFloat(board.width), H = CGFloat(board.height), S = CGFloat(board.scale)
let pixelsWide = Int(W * S), pixelsHigh = Int(H * S)
let sRGB = CGColorSpace(name: CGColorSpace.sRGB)!

func rgba(_ hex: String) -> NSColor {
    var value: UInt64 = 0
    Scanner(string: String(hex.dropFirst())).scanHexInt64(&value)
    let hasAlpha = hex.count == 9
    let r = CGFloat((value >> (hasAlpha ? 24 : 16)) & 0xff) / 255
    let g = CGFloat((value >> (hasAlpha ? 16 : 8)) & 0xff) / 255
    let b = CGFloat((value >> (hasAlpha ? 8 : 0)) & 0xff) / 255
    let a = hasAlpha ? CGFloat(value & 0xff) / 255 : 1
    return NSColor(srgbRed: r, green: g, blue: b, alpha: a)
}

// Alfred's Experimental Big Sur Dark theme, in points.
let windowWidth: CGFloat = 720, windowTop: CGFloat = 84, windowRadius: CGFloat = 15
let padH: CGFloat = 9, padV: CGFloat = 8, spacing: CGFloat = 8
let searchHeight: CGFloat = 58, searchRadius: CGFloat = 8
let rowHeight: CGFloat = 54, rowRadius: CGFloat = 8, iconSize: CGFloat = 40
let windowTint = rgba("#0000005B"), searchFill = rgba("#0000003E"), selectedFill = rgba("#358188FF")
let searchFont = NSFont.systemFont(ofSize: 34, weight: .light)
let titleFont = NSFont.systemFont(ofSize: 18)
let subtitleFont = NSFont.systemFont(ofSize: 12)
let shortcutFont = NSFont.systemFont(ofSize: 16)
let captionFont = NSFont.systemFont(ofSize: 15, weight: .semibold)

func makeContext() -> CGContext {
    CGContext(data: nil, width: pixelsWide, height: pixelsHigh, bitsPerComponent: 8, bytesPerRow: 0,
              space: sRGB, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
}

// The desktop: a dusk gradient with a few soft glows, drawn once, plus a blurred copy for
// the window's frosted glass.
func makeBackground() -> CGImage {
    let ctx = makeContext()
    ctx.scaleBy(x: S, y: S)
    let colors = ["#0E1A3AFF", "#2E2A6EFF", "#6A2F86FF", "#C24E7EFF", "#F08A5DFF"].map { rgba($0).cgColor }
    let gradient = CGGradient(colorsSpace: sRGB, colors: colors as CFArray, locations: [0, 0.35, 0.62, 0.85, 1])!
    ctx.drawLinearGradient(gradient, start: CGPoint(x: 0, y: H), end: CGPoint(x: W, y: 0), options: [])
    for (x, y, radius, hex) in [(W * 0.15, H * 0.2, 340.0, "#FF9E6B66"), (W * 0.85, H * 0.85, 380.0, "#4FD1C555"),
                                (W * 0.55, H * 0.05, 300.0, "#B06BFF44")] as [(CGFloat, CGFloat, CGFloat, String)] {
        let glow = CGGradient(colorsSpace: sRGB, colors: [rgba(hex).cgColor, rgba(hex).withAlphaComponent(0).cgColor] as CFArray,
                              locations: [0, 1])!
        ctx.drawRadialGradient(glow, startCenter: CGPoint(x: x, y: y), startRadius: 0,
                               endCenter: CGPoint(x: x, y: y), endRadius: radius, options: [])
    }
    return ctx.makeImage()!
}

func blurred(_ image: CGImage, radius: CGFloat) -> CGImage {
    let input = CIImage(cgImage: image)
    let blur = CIFilter(name: "CIGaussianBlur", parameters: [kCIInputImageKey: input.clampedToExtent(),
                                                             kCIInputRadiusKey: radius])!
    return CIContext().createCGImage(blur.outputImage!.cropped(to: input.extent), from: input.extent)!
}

let background = makeBackground()
let frosted = NSImage(cgImage: blurred(background, radius: 24 * S), size: NSSize(width: W, height: H))
var icons: [String: NSImage] = [:]

func draw(_ text: String, font: NSFont, color: NSColor, in rect: NSRect, align: NSTextAlignment = .left) {
    let style = NSMutableParagraphStyle()
    style.lineBreakMode = .byTruncatingTail
    style.alignment = align
    (text as NSString).draw(with: rect, options: [.usesLineFragmentOrigin, .truncatesLastVisibleLine],
                            attributes: [.font: font, .foregroundColor: color, .paragraphStyle: style])
}

func lineHeight(_ font: NSFont) -> CGFloat { ceil(font.ascender - font.descender + font.leading) }

func render(_ frame: Frame, to url: URL) {
    let ctx = makeContext()
    ctx.draw(background, in: CGRect(x: 0, y: 0, width: pixelsWide, height: pixelsHigh))
    ctx.translateBy(x: 0, y: CGFloat(pixelsHigh))
    ctx.scaleBy(x: S, y: -S)                                   // points, origin top left
    NSGraphicsContext.current = NSGraphicsContext(cgContext: ctx, flipped: true)

    // caption pill
    let caption = frame.caption as NSString
    let captionSize = caption.size(withAttributes: [.font: captionFont])
    let pill = NSRect(x: (W - captionSize.width) / 2 - 16, y: 22, width: captionSize.width + 32, height: 32)
    let pillPath = NSBezierPath(roundedRect: pill, xRadius: 16, yRadius: 16)
    rgba("#00000040").setFill(); pillPath.fill()
    rgba("#FFFFFF30").setStroke(); pillPath.lineWidth = 1; pillPath.stroke()
    draw(frame.caption, font: captionFont, color: .white,
         in: NSRect(x: pill.minX, y: pill.midY - lineHeight(captionFont) / 2, width: pill.width, height: lineHeight(captionFont)),
         align: .center)

    // window
    let rows = frame.rows.count
    let height = padV + searchHeight + (rows > 0 ? spacing + CGFloat(rows) * rowHeight : 0) + padV
    let window = NSRect(x: (W - windowWidth) / 2, y: windowTop, width: windowWidth, height: height)
    let windowPath = NSBezierPath(roundedRect: window, xRadius: windowRadius, yRadius: windowRadius)
    ctx.saveGState()
    ctx.setShadow(offset: CGSize(width: 0, height: -22 * S), blur: 60 * S, color: rgba("#00000088").cgColor)
    rgba("#00000066").setFill(); windowPath.fill()
    ctx.restoreGState()
    NSGraphicsContext.saveGraphicsState()
    windowPath.addClip()
    frosted.draw(in: NSRect(x: 0, y: 0, width: W, height: H), from: .zero, operation: .sourceOver, fraction: 1,
                 respectFlipped: true, hints: nil)
    windowTint.setFill(); windowPath.fill()
    NSGraphicsContext.restoreGraphicsState()
    rgba("#FFFFFF24").setStroke(); windowPath.lineWidth = 1; windowPath.stroke()

    // search field
    let field = NSRect(x: window.minX + padH, y: window.minY + padV, width: windowWidth - 2 * padH, height: searchHeight)
    searchFill.setFill(); NSBezierPath(roundedRect: field, xRadius: searchRadius, yRadius: searchRadius).fill()
    let textSize = (frame.query as NSString).size(withAttributes: [.font: searchFont])
    let textOrigin = NSPoint(x: field.minX + 12, y: field.midY - lineHeight(searchFont) / 2)
    if frame.selectAll && !frame.query.isEmpty {
        selectedFill.setFill()
        NSBezierPath(roundedRect: NSRect(x: textOrigin.x - 2, y: field.midY - 21, width: textSize.width + 4, height: 42),
                     xRadius: 4, yRadius: 4).fill()
    }
    (frame.query as NSString).draw(at: textOrigin, withAttributes: [.font: searchFont, .foregroundColor: NSColor.white])
    if frame.cursor {
        rgba("#FFFFFFE6").setFill()
        NSRect(x: textOrigin.x + textSize.width + 2, y: field.midY - 19, width: 2, height: 38).fill()
    }

    // results
    for (index, row) in frame.rows.enumerated() {
        let rect = NSRect(x: field.minX, y: field.maxY + spacing + CGFloat(index) * rowHeight, width: field.width, height: rowHeight)
        let selected = index == 0
        if selected {
            selectedFill.setFill(); NSBezierPath(roundedRect: rect, xRadius: rowRadius, yRadius: rowRadius).fill()
        }
        if icons[row.icon] == nil { icons[row.icon] = NSImage(contentsOfFile: row.icon) }
        if let icon = icons[row.icon] {
            icon.draw(in: NSRect(x: rect.minX + 8, y: rect.midY - iconSize / 2, width: iconSize, height: iconSize),
                      from: .zero, operation: .sourceOver, fraction: 1, respectFlipped: true, hints: nil)
        }
        let textX = rect.minX + 8 + iconSize + 12
        let shortcutWidth: CGFloat = 44
        let textWidth = rect.maxX - 12 - shortcutWidth - textX
        let titleHeight = lineHeight(titleFont), subtitleHeight = lineHeight(subtitleFont)
        let top = rect.midY - (titleHeight + 1 + subtitleHeight) / 2
        draw(row.title, font: titleFont, color: selected ? .white : rgba("#FFFFFFCB"),
             in: NSRect(x: textX, y: top, width: textWidth, height: titleHeight))
        draw(row.subtitle, font: subtitleFont, color: selected ? rgba("#FFFFFFCB") : rgba("#FFFFFF7E"),
             in: NSRect(x: textX, y: top + titleHeight + 1, width: textWidth, height: subtitleHeight))
        draw(selected ? "↩" : "⌘\(index + 1)", font: shortcutFont, color: selected ? .white : rgba("#FFFFFF7E"),
             in: NSRect(x: rect.maxX - 12 - shortcutWidth, y: rect.midY - lineHeight(shortcutFont) / 2,
                        width: shortcutWidth, height: lineHeight(shortcutFont)), align: .right)
    }

    NSGraphicsContext.current = nil
    let destination = CGImageDestinationCreateWithURL(url as CFURL, "public.png" as CFString, 1, nil)!
    CGImageDestinationAddImage(destination, ctx.makeImage()!, nil)
    CGImageDestinationFinalize(destination)
}

var list = "ffconcat version 1.0\n"
for (index, frame) in board.frames.enumerated() {
    let name = String(format: "frame%03d.png", index)
    render(frame, to: output.appendingPathComponent(name))
    list += "file '\(name)'\nduration \(frame.duration)\n"
}
// the concat demuxer only honours the last duration when the last file is listed twice
list += "file '\(String(format: "frame%03d.png", board.frames.count - 1))'\n"
try! list.write(to: output.appendingPathComponent("frames.ffconcat"), atomically: true, encoding: .utf8)
print("\(board.frames.count) frames")
