import time

#Looks at a post to determine if it's a duplicate. This class is more for future scalability and organization than for practical use at the moment
class DuplicatePost(object):


    def __init__(self, newSubmission, oldPosts, reddit, checkedComments, priorOffenders):
        self.newSubmission = newSubmission
        self.oldPosts = oldPosts
        self.copiedComments = []
        self.checkedNewComments = []
        self.candidatesForCopying = []
        self.priorOffenders = priorOffenders
        self.checkedComments = checkedComments


        #Posts with fewer than this many words aren't looked at
        self.MINPOSTLENGTH = 15

        #The number of comments in the new post it looks at
        self.NUMCOMMENTSTOCHECK = 20

        #The number of original comments it pulls out of the search results
        self.DEPTHOFORIGINALCOMMENTSEARCH = 10

        self.findCandidatesForCopying()
        self.checkTopComments()


    #used for only looking at the first MINPOSTLENGTH words of a comment
    def truncateComment(self, comment):
        splitString = comment.body.split()
        truncatedBody = ""
        for i in range(self.MINPOSTLENGTH):
            truncatedBody = truncatedBody + splitString[i] + " "
        return truncatedBody

    #Looks at old posts with similar titles and grabs the top comments
    def findCandidatesForCopying(self):
        for aPost in self.oldPosts:
            time.sleep(0.5)
            oldComments = aPost.comments
            for i in range(self.DEPTHOFORIGINALCOMMENTSEARCH):
                if len(oldComments[i].body.split()) >= self.MINPOSTLENGTH:
                    self.candidatesForCopying.append(oldComments[i])

    #Checks the top NUMCOMMENTSTOCHECK comments in a the new post
    def checkTopComments(self):
        for aNewComment in self.newSubmission.comments[:self.NUMCOMMENTSTOCHECK]:
            try:
                if self.checkedComments[aNewComment.id] != None:
                    return
            except:
                pass


            if len(aNewComment.body.split()) > self.MINPOSTLENGTH:
                self.checkComment(aNewComment)



    #Check that a comment is a duplicate of another
    def checkComment(self, comment):
        if "u/" in comment.body or "posted" in comment.body:
            return

        commentArray = comment.body.split()[:self.MINPOSTLENGTH]

        #splits the comment into an array of words and checks how many words it has in common with an old comment.
        for anOriginalComment in self.candidatesForCopying:
            originalCommentArray = anOriginalComment.body.split()[:self.MINPOSTLENGTH]
            matchCounter = 0
            for aWord in commentArray:
                if aWord in originalCommentArray:
                    matchCounter += 1
            if matchCounter > (self.MINPOSTLENGTH - 2) and anOriginalComment.author != comment.author:
                print "We found one, boss!"
                print comment.body + "\n"
                print anOriginalComment.body

                try:
                    self.priorOffenders[str(comment.author)] += 1
                except:
                    self.priorOffenders[str(comment.author)] = 1

                newCopy = CopiedComment(originalComment=anOriginalComment, newComment=comment, priorOffenders=self.priorOffenders)
                self.copiedComments.append(newCopy)
                newCopy.reportToTheMods()


        self.checkedNewComments.append(comment)




class CopiedComment(object):
    def __init__(self, originalComment, newComment, priorOffenders):
        self.originalComment = originalComment
        self.newComment = newComment
        self.priorOffenders = priorOffenders

    #Send a message to the mods
    def reportToTheMods(self):
        originalCommentUrl = self.originalComment.submission.url + str(self.originalComment.name)[3:]
        copiedCommentUrl = self.newComment.submission.url + str(self.newComment.name)[3:]

        myComment = "Found a reposted comment: \n\n"
        myComment += "/u/"+str(self.newComment.author) + " stole [this comment]({}) from ".format(copiedCommentUrl)
        myComment += "[here]({}). ".format(originalCommentUrl)

        #For repeat offenders
        if self.priorOffenders[str(self.newComment.author)] > 1:
            myComment += "\n\nThis isn't the first time. Number of times /u/{} has tried to pull this shit: {}.".format(str(self.newComment.author), self.priorOffenders[str(self.newComment.author)])


        #TODO: Actually make this message get sent to the mods
        print"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n\n"
        print myComment
        print"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n\n"



    def revealTheCharlatan(self):
        #don't forget that function name!
        originalCommentUrl = self.originalComment.submission.url + str(self.originalComment.name)[3:]
        myComment = "WEEEOOOOO WEEEEOOOOO! \n\n"
        myComment += "/u/"+str(self.newComment.author) + " is a big fat phony who stole this comment from "
        myComment += "[here]({}). ".format(originalCommentUrl)
        myComment += "He's going to karma jail, which is like normal jail, except it's not real."
        myComment += "\n\n---\n\n"
        myComment += "*Bleep Bloop! If you think I've booked the wrong guy, send me a message so my owner can fix me.*"
        print myComment

        #This posts the reply, though I should note that certain subreddits don't allow bots and will shadowdelete these comments
        self.newComment.reply(myComment)