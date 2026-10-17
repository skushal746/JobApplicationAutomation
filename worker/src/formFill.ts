import type { Page } from 'playwright-core'
import { log } from './log'

// Labels the worker must never touch: bot traps, and statements only you can make.
const NEVER_FILL = /honey ?pot|agree|terms|consent|certif|attest|signature|i acknowledge/i

/**
 * Fills visible, empty text inputs, textareas and native selects whose label exactly
 * matches a key in `fields`. Returns the labels it filled. Checkboxes, radios and
 * custom dropdown widgets are left for you.
 */
export async function fillKnownFields(page: Page, fields: Record<string, string>): Promise<string[]> {
  const filled: string[] = []

  for (const [label, value] of Object.entries(fields)) {
    if (NEVER_FILL.test(label)) {
      log.warn(`Skipping profile field "${label}": the worker never fills agreements or bot traps`)
      continue
    }
    // Exact label, ignoring case and a trailing required-field asterisk ("First Name *").
    const escaped = label.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const matches = page.getByLabel(new RegExp(`^\\s*${escaped}\\s*\\*?\\s*$`, 'i'))
    const count = await matches.count()

    for (let i = 0; i < count; i++) {
      const field = matches.nth(i)
      try {
        if (!(await field.isVisible()) || !(await field.isEditable())) continue
        const { tag, type } = await field.evaluate(el => ({
          tag: el.tagName,
          type: (el as HTMLInputElement).type ?? '',
        }))

        if (tag === 'SELECT') {
          await field.selectOption({ label: value })
          filled.push(label)
        } else if ((tag === 'INPUT' || tag === 'TEXTAREA') && !['checkbox', 'radio', 'file', 'hidden'].includes(type)) {
          if ((await field.inputValue()) !== '') continue // keep what the site or resume parser filled
          await field.fill(value)
          filled.push(label)
        }
      } catch (err) {
        log.warn(`Could not fill "${label}":`, err instanceof Error ? err.message.split('\n')[0] : err)
      }
    }
  }
  return filled
}

/** Uploads the resume into the first file input on the page, if there is one. */
export async function uploadResume(page: Page, resumePath: string): Promise<boolean> {
  const input = page.locator('input[type="file"]').first()
  if ((await input.count()) === 0) return false
  await input.setInputFiles(resumePath)
  return true
}

// Runs inside the web page. Kept as plain JavaScript text on purpose: tsx compiles named
// helper functions into calls to its own __name() helper, which does not exist in the page.
const LIST_EMPTY_FIELDS_SCRIPT = `(() => {
  function labelFor(el) {
    var id = el.getAttribute('id');
    var byFor = id ? document.querySelector('label[for="' + CSS.escape(id) + '"]') : null;
    var refs = (el.getAttribute('aria-labelledby') || '').split(' ').filter(Boolean);
    var byAria = refs.map(function (r) { var n = document.getElementById(r); return n ? n.textContent.trim() : ''; }).filter(Boolean).join(' ');
    return ((byFor && byFor.textContent) || el.getAttribute('aria-label') || byAria || '').trim();
  }
  function visible(el) {
    var r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  }
  var skipTypes = ['hidden', 'checkbox', 'radio', 'file', 'submit', 'button'];
  var labels = Array.from(document.querySelectorAll('input, textarea, select'))
    .filter(function (el) { return skipTypes.indexOf(el.type) === -1 && visible(el) && !el.disabled && el.value === ''; })
    .map(labelFor)
    .filter(function (l) { return l && !/honey ?pot|ask me something/i.test(l); });
  return Array.from(new Set(labels));
})()`

/** Labels of visible fields that are still empty: what you need to add to profile.json or fill by hand. */
export async function listEmptyFields(page: Page): Promise<string[]> {
  return page.evaluate(LIST_EMPTY_FIELDS_SCRIPT) as Promise<string[]>
}

/** Oracle shows an idle-session dialog; keep the session alive while the worker or you are working. */
export async function keepSessionAlive(page: Page) {
  const button = page.getByRole('button', { name: /^continue working$/i })
  if (await button.isVisible().catch(() => false)) await button.click().catch(() => {})
}
