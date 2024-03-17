// HIGHLIGHT TEXT WITH SEARCH TERM
function highlightText (input: string, fontWeight: number, highlightTerm: string) {
  if (highlightTerm === '') return input

  const startIndex = input.toLowerCase().indexOf(highlightTerm.toLowerCase())
  if (startIndex >= 0) {
    const endIndex = startIndex + highlightTerm.length

    return (
            <span>
                {input.slice(0, startIndex).toString()}
                <span
                    style={{
                      fontWeight: fontWeight + 200,
                      textDecoration: 'underline'
                    }}
                >
                    {input.slice(startIndex, endIndex).toString()}
                </span>
                {input.slice(endIndex).toString()}
            </span>
    )
  }

  return input
}

export default {
  highlightText
}
