module.exports = async ({ github, context }) => {
  const fs = require('fs')

  const artifacts = await github.rest.actions.listWorkflowRunArtifacts({
    owner: context.repo.owner,
    repo: context.repo.repo,
    run_id: context.payload.workflow_run.id,
  })
  const [matchArtifact] = artifacts.data.artifacts.filter((artifact) =>
    artifact.name == "typeshed_primer_errors")
  const download = await github.rest.actions.downloadArtifact({
    owner: context.repo.owner,
    repo: context.repo.repo,
    artifact_id: matchArtifact.id,
    archive_format: "zip",
  })

  fs.writeFileSync("errors.zip", Buffer.from(download.data));
}
