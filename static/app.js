document.getElementById("clip-container").addEventListener("click", delegateEvent);

function delegateEvent(e){
    let target = e.target
    if (target.id == "like"){
        likeClip(target)
    }
    if (target.id == "dislike"){
        unlikeClip(target)
    }

}

function likeClip(target) {
    btn = target
    form = btn.parentNode
    target.innerHTML = '<i class="fas fa-spinner"></i> Like'
    axios.post(`/clips/${btn.dataset.clip_id}/vote/add`)
      .then(function () {
        form.innerHTML = `<button id="dislike" data-clip_id="${btn.dataset.clip_id}" class="btn btn-danger m-1"><i class="fas fa-thumbs-down"></i></i> Dislike</button>`
      })
      .catch(function (error) {
        console.log(error);
        form.innerHTML = `<button id="like" data-clip_id="${btn.dataset.clip_id}" class="btn btn-primary m-1"><i class="fas fa-thumbs-up"></i></i> Like</button>`
      });
}

function unlikeClip(target) {
    btn = target
    form = btn.parentNode
    target.innerHTML = '<i class="fas fa-spinner"></i> Dislike'
    axios.post(`/clips/${btn.dataset.clip_id}/vote/delete`)
      .then(function () {
        form.innerHTML = `<button id="like" data-clip_id="${btn.dataset.clip_id}" class="btn btn-primary m-1"><i class="fas fa-thumbs-up"></i></i> Like</button>`
      })
      .catch(function (error) {
        console.log(error);
        form.innerHTML = `<button id="dislike" data-clip_id="${btn.dataset.clip_id}" class="btn btn-danger m-1"><i class="fas fa-thumbs-down"></i></i> Dislike</button>`
      });
}