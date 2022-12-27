module.exports = async ({ github, context }) => {
  const fs = require('fs')

  let data = fs.readFileSync('errors.txt', { encoding: 'utf8' })
  // posting comment fails if too long, so truncate
  if (data.length > 30000) {
    let truncated_data = data.substring(0, 30000)
    let lines_truncated = data.split('\n').length - truncated_data.split('\n').length
    data = truncated_data + `\n\n... (truncated ${lines_truncated} lines) ...\n`
  }

  const body = data.trim()
    ? '⚠ This change produces Flake8 errors in typeshed: \n```' + data + '```'
    : 'This change has no effect on typeshed. 🤖🎉'
  const issue_number = parseInt(fs.readFileSync("pr_number.txt", { encoding: "utf8" }))
  await github.rest.issues.createComment({
    issue_number,
    owner: context.repo.owner,
    repo: context.repo.repo,
    body
  })

  return issue_number
}
