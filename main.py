import praw
import time
import json
from PotentialDuplicate import DuplicatePost


#Look at the praw documentation to see how to set up a bot with an existing reddit account. You'll need another
#file and to change bot1 to whatever you name your bot.
reddit = praw.Reddit('bot1')

#An array saying which subs to check
mySubs = ["askreddit"]

#Load records of prior offenders, which comments I've checked and which posts don't need to be checked again.
#Note that there doesn't exist a current way of dumping these files because it hasn't come up yet, but it would
#be necessary after a while
try:
    priorOffenders = json.load(open("priorOffenders.txt",'r'))
except:
    priorOffenders = {}
    print "Failed to load prior offenders or the file does not exist."

try:
    checkedComments = json.load(open("checkedComments.txt",'r'))
except:
    checkedComments = {}
    print "Failed to load checked comments or the file does not exist."


try:
    originalPosts = json.load(open("originalPosts.txt",'r'))
except:
    originalPosts = {}
    print "Failed to load original posts or the file does not exist."



#This essentially runs the bot. It looks through the subreddits you give it to check out for copied comments on posts with similar titles
def crawlThroughSubreddits(subreddits):

    # go through
    for aSub in mySubs:

        subreddit = reddit.subreddit(aSub)
        print "Checking Hot on {}".format(aSub)
        time.sleep(0.5)
        for submission in subreddit.hot(limit=20):
            checkSubmisison(submission, subreddit)


    json.dump(originalPosts, open("originalPosts.txt",'w'))
    json.dump(checkedComments, open("checkedComments.txt",'w'))
    json.dump(priorOffenders, open("priorOffenders.txt",'w'))


#To check a submission
def checkSubmisison(submission, subreddit):
    postTimeHours = (time.time() - submission.created_utc) / (60*60)


    #Skip submissions that are old, don't have enough comments, or are stickied
    if submission.stickied or len(submission.comments) < 20 or postTimeHours > 18:
        return


    #skip askreddit submissions that have fun facts
    if "quote" in submission.title or "fact" in submission.title:
        return

    #check in originalPosts to see if the post already exists
    try:
        if originalPosts[submission.id] == 1:
            print submission.title + " is original"
            return
    except:
        pass

    #Wait so we don't exceed our request limit
    time.sleep(.5)

    #Look to see if there are posts with similar titles
    list = subreddit.search(submission.title, limit=4)
    similarSubmissions = []
    while 1:
        try:
            nextSubmission = list.next()
        except:
            break

        #Rule out posts with few comments and any search result that is the post itself
        if nextSubmission.id != submission.id and len(nextSubmission.comments) > 19:
            similarSubmissions.append(nextSubmission)

    if len(similarSubmissions) != 0:

        #create an instance of DuplicatePost that holds the copied submission
        newDuplicate = DuplicatePost(newSubmission=submission, oldPosts=similarSubmissions, reddit=reddit, priorOffenders= priorOffenders, checkedComments=checkedComments)


        for aComment in newDuplicate.checkedNewComments:
            checkedComments[aComment.id] = aComment.created

    else:
        originalPosts[submission.id] = 1


crawlThroughSubreddits(mySubs)
