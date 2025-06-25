export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

export class Logger {
  private level: LogLevel;
  private prefix: string;

  constructor(prefix: string = "OF", level: LogLevel = LogLevel.INFO) {
    this.prefix = prefix;
    this.level = level;
  }

  private log(level: LogLevel, message: string, ...args: unknown[]): void {
    if (level < this.level) return;
    
    const timestamp = new Date().toISOString();
    const levelStr = LogLevel[level];
    const logPrefix = `[${timestamp}] [${levelStr}] [${this.prefix}]`;
    
    switch (level) {
      case LogLevel.DEBUG:
        console.error(logPrefix, message, ...args);
        break;
      case LogLevel.INFO:
        console.error(logPrefix, message, ...args);
        break;
      case LogLevel.WARN:
        console.warn(logPrefix, message, ...args);
        break;
      case LogLevel.ERROR:
        console.error(logPrefix, message, ...args);
        break;
    }
  }

  debug(message: string, ...args: unknown[]): void {
    this.log(LogLevel.DEBUG, message, ...args);
  }

  info(message: string, ...args: unknown[]): void {
    this.log(LogLevel.INFO, message, ...args);
  }

  warn(message: string, ...args: unknown[]): void {
    this.log(LogLevel.WARN, message, ...args);
  }

  error(message: string, ...args: unknown[]): void {
    this.log(LogLevel.ERROR, message, ...args);
  }
}

// Default to DEBUG level for development, configurable via environment
const getLogLevel = (): LogLevel => {
  const envLevel = Deno.env.get("LOG_LEVEL")?.toUpperCase();
  switch (envLevel) {
    case "DEBUG": return LogLevel.DEBUG;
    case "INFO": return LogLevel.INFO;
    case "WARN": return LogLevel.WARN;
    case "ERROR": return LogLevel.ERROR;
    default: return LogLevel.DEBUG; // Default to DEBUG for development
  }
};

export const logger = new Logger("OF", getLogLevel());