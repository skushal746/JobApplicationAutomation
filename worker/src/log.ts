function stamp() {
  return new Date().toLocaleString()
}

export const log = {
  info: (...args: unknown[]) => console.log(`[${stamp()}]`, ...args),
  warn: (...args: unknown[]) => console.warn(`[${stamp()}] WARN`, ...args),
  error: (...args: unknown[]) => console.error(`[${stamp()}] ERROR`, ...args),
  /** Something the person at the keyboard needs to do in the browser window. */
  action: (message: string) => console.log(`\n[${stamp()}] >>> ACTION NEEDED: ${message}\n`),
}
