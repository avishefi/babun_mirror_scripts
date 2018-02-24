#!/bin/bash
set -eu # fail on errors and undefined variables
mirror="${1}"
cygDist="${2}"
mirrorParallelism="${3:-3}"

parallel_rsync() {
  rsyncJobs="${1}"
  sourceDir="${2}"
  targetDir="${3}"

  parallel --verbose --progress -j "${rsyncJobs}" --delay 5 \
           --joblog parallel_rsync_job.log --results {}_results \
           rsync --files-from={} -va --delete --delete-excluded --delete-after \
           --exclude='*mail-archives*' --exclude='*src.tar.bz2' --exclude='*src.tar.xz' \
           "${sourceDir}" "${targetDir}"
}


mkdir -p ${cygDist}

TMPDIR=$(mktemp -d)
(
  cd ${TMPDIR}
  filesList="${TMPDIR}/files.lst"
  chunkPrefix="chunk."
  chunkSplits=30

  echo "Creating file list"
  rsync -va --no-motd --dry-run --exclude='*mail-archives*' --exclude='*src.tar.bz2' --exclude='*src.tar.xz' \
        --exclude='x86_64/' ${mirror} ${cygDist} | head --lines=-3 | tail --lines=+3 > ${filesList}
  echo "Found $(wc -l ${filesList}) files and directories"

  echo "Splitting ${filesList} into ${chunkSplits} chunks"
  split --number="l/${chunkSplits}" ${filesList} ${chunkPrefix}

  echo "Executing parallel rsync (jobs=${mirrorParallelism}) ${mirror} ${cygDist}"
  find . -type f -name "${chunkPrefix}*" | parallel_rsync ${mirrorParallelism} ${mirror} ${cygDist}
)


echo "Done"
