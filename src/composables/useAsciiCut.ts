/** 'down': black pours away (landing, page cuts); 'up': black rises back over the page, then onCovered */
export interface CutOptions { dir?: 'down' | 'up'; onCovered?: () => void }

/** Handle to the full-screen ASCII cut (AsciiCut.vue registers play()). */
export const asciiCut = { play: (_opts?: CutOptions) => {} }
