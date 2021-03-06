payload='''{
  "sha": "d0e1b1f82ddd1f2c42afbe15f624b120db66fbb4",
  "url": "https://api.github.com/repos/adsabs/adsws/git/commits/d0e1b1f82ddd1f2c42afbe15f624b120db66fbb4",
  "html_url": "https://github.com/adsabs/adsws/commit/d0e1b1f82ddd1f2c42afbe15f624b120db66fbb4",
  "author": {
    "name": "Vladimir Sudilovsky",
    "email": "vsudilovsky@gmail.com",
    "date": "2015-07-23T19:10:34Z"
  },
  "committer": {
    "name": "Vladimir Sudilovsky",
    "email": "vsudilovsky@gmail.com",
    "date": "2015-07-23T19:10:34Z"
  },
  "tree": {
    "sha": "69b861ea3eaaac9ce895bfea6eca3ccd4ac0c35e",
    "url": "https://api.github.com/repos/adsabs/adsws/git/trees/69b861ea3eaaac9ce895bfea6eca3ccd4ac0c35e"
  },
  "message": "Merge branch 'issue#72'",
  "parents": [
    {
      "sha": "dc476fa3ec5557bee014943f6e40bb2ab7f87f36",
      "url": "https://api.github.com/repos/adsabs/adsws/git/commits/dc476fa3ec5557bee014943f6e40bb2ab7f87f36",
      "html_url": "https://github.com/adsabs/adsws/commit/dc476fa3ec5557bee014943f6e40bb2ab7f87f36"
    },
    {
      "sha": "efd61c3a0422eef8e84755fb57e9e9f892a6e0b5",
      "url": "https://api.github.com/repos/adsabs/adsws/git/commits/efd61c3a0422eef8e84755fb57e9e9f892a6e0b5",
      "html_url": "https://github.com/adsabs/adsws/commit/efd61c3a0422eef8e84755fb57e9e9f892a6e0b5"
    }
  ]
}'''

payload_tag = '''{
  "ref": "refs/tags/v1.0.0",
  "url": "https://api.github.com/repos/adsabs/adsws/git/refs/tags/v1.0.0",
  "object": {
    "sha": "unnitest-tag-commit",
    "type": "tag",
    "url": "https://api.github.com/repos/adsabs/adsws/git/tags/d0e1b1f82ddd1f2c42afbe15f624b120db66fbb4"
  }
}'''

payload_get_tag = '''{
  "sha": "unnitest-tag-commit",
  "url": "https://api.github.com/repos/adsabs/governor/git/tags/unnitest-tag-commit",
  "tagger": {
    "name": "adsabs",
    "email": "adshelp@cfa.harvard.edu",
    "date": "2015-08-19T14:52:49Z"
  },
  "object": {
    "sha": "unittest-commit",
    "type": "commit",
    "url": "https://api.github.com/repos/adsabs/governor/git/commits/2a047ead58a3a87b46388ac67fe08c944c3230e0"
  },
  "tag": "v1.0.0",
  "message": "First version release 1.0.0"
}'''

payload_tag_fail = '''{
  "message": "Not Found",
  "documentation_url": "https://developer.github.com/v3"
}'''