export function safeFocusNoScroll(element) {
  if (!element) return false;
  try {
    if (element.tabIndex === undefined || element.tabIndex < 0) {
      element.tabIndex = -1;
    }
    element.focus({ preventScroll: true });
    return true;
  } catch (e) {
    try {
      element.focus();
      return true;
    } catch (err) {
      return false;
    }
  }
}
