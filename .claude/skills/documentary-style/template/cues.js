// Cue times (s) measured from the voiceover (assets/vo.mp3, 25.63 s).
// Phrase edges from silence detection; key word onsets checked against the
// RMS energy envelope (20 ms windows).
window.CUES = {
  duration: 26.5,     // voice + short hold on the final frame
  y2011: 0.15,        // "In 2011"
  videos: 3.43,       // "...a collection of videos"
  compound: 4.97,     // "compound"
  abbottabad: 5.30,   // "Abbottabad"
  pakistan: 6.05,     // "Pakistan"
  l2: 7.55,           // "Six years later,"
  published: 9.46,    // "published"
  l2end: 10.83,
  cars: 11.98,        // "Cars"
  chicken: 12.64,     // "Chicken Little"
  antz: 13.62,        // "and Antz"
  l4: 14.59,          // "But scroll to the very last title."
  scroll: 14.80,
  l4end: 16.40,
  l5: 16.87,          // "It's a documentary called..."
  title: 18.52,       // "Where in the World Is Osama bin Laden?"
  titleEnd: 20.59,
  l6: 21.15,          // "A copy of the film..."
  search1: 23.09,
  place: 24.20,       // "the very place"
  ended: 25.03,       // "ended"
  voiceEnd: 25.41,
};
