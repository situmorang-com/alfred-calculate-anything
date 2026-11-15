// alfredctl: helper for testing Alfred workflows from a terminal session.
//
// Build it outside the workflow folder:
//     swiftc -O -o "$TMPDIR/alfredctl" tools/alfredctl.swift
//
//   window               Print "<window id> <x> <y> <width> <height>" for each Alfred window on screen.
//                        Exit status 1 when none is open.
//   field                Print the text in Alfred's search field (needs Accessibility permission).
//                        Exit status 1 when it cannot be read.
//   key <keycode>        Press and release one key, delivered to Alfred only.
//                        36 Return, 53 Escape, 125 Down, 126 Up.
//   modreturn <cmd|alt>  Return with Command or Option held. Alfred reads held modifiers from the
//                        session's keyboard state, so the modifier is pressed at session level for about
//                        a tenth of a second and then released: a key the owner presses in that moment
//                        gets the modifier too. Return itself goes to Alfred only.
//   pbsave <file>        Save every clipboard item, in every type, to <file>.
//   pbrestore <file>     Put a saved clipboard back.
//
// The procedure and its guard rails are in docs/MEMORY.md, "Live testing in Alfred".
import Cocoa
import CoreGraphics

func fail(_ message: String, _ status: Int32 = 2) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8))
    exit(status)
}

let usage = "usage: alfredctl window | field | key <keycode> | modreturn <cmd|alt> | pbsave <file> | pbrestore <file>"
let args = Array(CommandLine.arguments.dropFirst())
guard let command = args.first else { fail(usage) }

// MARK: - Clipboard (Alfred not needed)

if command == "pbsave" || command == "pbrestore" {
    guard args.count == 2 else { fail(usage) }
    let url = URL(fileURLWithPath: args[1])
    let board = NSPasteboard.general
    if command == "pbsave" {
        var saved: [[String: Data]] = []
        for item in board.pasteboardItems ?? [] {
            var entry: [String: Data] = [:]
            for type in item.types {
                if let data = item.data(forType: type) { entry[type.rawValue] = data }
            }
            saved.append(entry)
        }
        do {
            let data = try PropertyListSerialization.data(fromPropertyList: saved, format: .binary, options: 0)
            try data.write(to: url)
        } catch {
            fail("pbsave: \(error.localizedDescription)", 1)
        }
        print("saved \(saved.count) item(s)")
    } else {
        var saved: [[String: Data]] = []
        do {
            let data = try Data(contentsOf: url)
            guard let list = try PropertyListSerialization.propertyList(from: data, options: [], format: nil)
                as? [[String: Data]] else { fail("pbrestore: not a saved clipboard", 1) }
            saved = list
        } catch {
            fail("pbrestore: \(error.localizedDescription)", 1)
        }
        board.clearContents()
        let items = saved.map { entry -> NSPasteboardItem in
            let item = NSPasteboardItem()
            for (type, value) in entry { item.setData(value, forType: NSPasteboard.PasteboardType(type)) }
            return item
        }
        if !items.isEmpty && !board.writeObjects(items) { fail("pbrestore: the clipboard refused the items", 1) }
        print("restored \(items.count) item(s)")
    }
    exit(0)
}

// MARK: - Alfred

guard let alfred = NSWorkspace.shared.runningApplications.first(where: {
    $0.bundleIdentifier == "com.runningwithcrayons.Alfred"
}) else { fail("Alfred is not running", 3) }
let pid = alfred.processIdentifier

switch command {
case "window":
    let options: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
    let list = (CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]]) ?? []
    var found = false
    for window in list {
        guard let owner = window[kCGWindowOwnerPID as String] as? Int, owner == Int(pid),
              let number = window[kCGWindowNumber as String] as? Int,
              let raw = window[kCGWindowBounds as String] as? [String: Any],
              let bounds = CGRect(dictionaryRepresentation: raw as CFDictionary),
              bounds.width >= 200, bounds.height >= 30 else { continue }
        print("\(number) \(Int(bounds.minX)) \(Int(bounds.minY)) \(Int(bounds.width)) \(Int(bounds.height))")
        found = true
    }
    exit(found ? 0 : 1)

case "field":
    func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
        var value: CFTypeRef?
        return AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success ? value : nil
    }
    func searchText(in element: AXUIElement, depth: Int) -> String? {
        let role = attribute(element, kAXRoleAttribute) as? String ?? ""
        if role == kAXTextFieldRole || role == kAXTextAreaRole,
           let text = attribute(element, kAXValueAttribute) as? String {
            return text
        }
        guard depth > 0, let children = attribute(element, kAXChildrenAttribute) as? [AXUIElement] else {
            return nil
        }
        for child in children {
            if let text = searchText(in: child, depth: depth - 1) { return text }
        }
        return nil
    }
    let windows = attribute(AXUIElementCreateApplication(pid), kAXWindowsAttribute) as? [AXUIElement] ?? []
    for window in windows {
        if let text = searchText(in: window, depth: 6) {
            print(text)
            exit(0)
        }
    }
    exit(1)

case "key":
    guard args.count == 2, let code = UInt16(args[1]) else { fail(usage) }
    let source = CGEventSource(stateID: .hidSystemState)
    for down in [true, false] {
        guard let event = CGEvent(keyboardEventSource: source, virtualKey: code, keyDown: down) else {
            fail("could not create the key event", 4)
        }
        event.flags = []
        event.postToPid(pid)
        usleep(40_000)
    }
    exit(0)

case "modreturn":
    let modifiers: [String: (key: UInt16, flag: CGEventFlags)] = [
        "cmd": (55, .maskCommand),
        "alt": (58, .maskAlternate),
    ]
    guard args.count == 2, let modifier = modifiers[args[1]] else { fail(usage) }
    let source = CGEventSource(stateID: .combinedSessionState)
    func setModifier(down: Bool) {
        guard let event = CGEvent(keyboardEventSource: source, virtualKey: modifier.key, keyDown: down) else { return }
        event.type = .flagsChanged
        event.flags = down ? modifier.flag : []
        event.post(tap: .cgSessionEventTap)
    }
    setModifier(down: true)
    usleep(70_000)
    for down in [true, false] {
        if let event = CGEvent(keyboardEventSource: source, virtualKey: 36, keyDown: down) {
            event.flags = modifier.flag
            event.postToPid(pid)
        }
        usleep(25_000)
    }
    usleep(30_000)
    // Released explicitly: exit() skips Swift's `defer`, which would leave the modifier held.
    setModifier(down: false)
    usleep(20_000)
    setModifier(down: false)
    exit(0)

default:
    fail(usage)
}
