/** https://stackoverflow.com/a/34602679/6335363 */
function redirectToTz() {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  document.location.pathname = `/${tz}`;
}

redirectToTz();
