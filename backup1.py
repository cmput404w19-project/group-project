    # postList = Post.objects.all()
    user = UserProfile.objects.filter(user_id = request.user).first()
    # TODO filter posts in such a way that we can see only the ones we need
    # All post that can see
    # PUBLIC post
    public_post = Post.objects.filter(visibility="PUBLIC").all()
    for post in public_post:
        postList.append({"p":post})
    # users own post
    own_post = Post.objects.filter(user_id=user.author_id).exclude(visibility="PUBLIC").all()
    for post in own_post:
        postList.append({"p":post})
    # see friends post  (private to friends)
    # get a list of friends userprofile object
    friends_userprofile = find_friends(user)
    for friend in friends_userprofile:
        # get all the friends private post
        friendPrivatePosts = Post.objects.filter(visibility="FRIENDS", user_id=friend).all()
        for post in friendPrivatePosts:
            postList.append({"p":post})
    # see friends post's that is visible to me (private to certain users, and I am one of them who can see it)
    all_visible_post_object = PostVisibleTo.objects.filter(user_id=user.author_id).all()
    for i in all_visible_post_object:
        post = Post.objects.filter(post_id=i.post_id.post_id).first()
        postList.append({"p":post})
    # see friends of friends post

    # see our own server's post

    # sort posts by publish_time
    #print(type(postList))
    #print(postList[0]['p'].publish_time < postList[1]['p'].publish_time)
    if(len(postList) > 1):
        for i in range(0,len(postList)):
            for j in range(0,len(postList)-i-1):
                if(postList[j]['p'].publish_time < postList[j+1]['p'].publish_time):
                    (postList[j],postList[j+1])=(postList[j+1],postList[j])


    # now get the comments(comment list) of each post that is visible to this user
    for post in postList:
        post["cl"] = Comment.objects.filter(post_id=post["p"].post_id).order_by("publish_time").all()



# TODO we need a way to somehow get the comment objects for each specific post
# and then add that list of comment objects to that post object
# so that we can render the post and the comment belong to that post correctly
user = request.user
if request.user.is_authenticated:
    profile = UserProfile.objects.filter(user_id = request.user).first()
    context = {'list': postList, 'userprofile_id': profile.author_id, 'user':user}
else:
    context = {'list': postList}