# Booru Collection Crawler

## What do we crawl?
- Post
  - image file( as high-res as possible)
  - tags to describe this picture

## How do we arrange the crawling process

### When start from sketch
- User input the search condition
- create a task folder named based on the user input search condition
- crawl the complete post resource identifier(such as its url) list of all posts(traverse all the pagination of the website), and store it to task folder.
- from list top to bottom
  - attach a status field to the ListItem in the list(for resuming from breakpoint if error occurs)
  - download and store each post(including its image and tags) to task folder. You should name the image name based on its identifier on the website, such as its post id.
  - depending on the download result:
    - if success, mark the ListItem status as `COMPLETE`
    - if fail, mark the ListItem status as `FAIL`, to help the crawler recognize it as the breakpoint where we should resume next time

### When resume from breakpoint
- User select a task foler that not yet completed
- traverse through the post list, find all those breakpoints whose statuses are not `COMPLETE`
- resume the crawling process from breakpoints

## Some tips
- dont use streaming to download the image, download it in memory first, NOT until its content is complete should you transfer it into dist.
- set a throttle timer between each request to the website server lest we were to caught by the web crawler firewall
- when error occurs from the reponse the website server:
  - If the status code equals to 410, 403 or something related to server intentionaly refuse the request, HANG the working process, ask the User to manually handle the situation
  - If the error reason is unclear(such as TCP connect reset, timeout or other network issues), retry the request automatically, also set yourself a `maxRetryTime` to avoid endless futile trials