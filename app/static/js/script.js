function setBackgroundImage(image_url) {
  if (image_url) {
    console.log(image_url)
    document.body.style.backgroundImage = `url('${image_url}')`;
    document.body.style.backgroundSize = "cover";
    document.body.style.backgroundRepeat = "no-repeat";
    document.body.style.backgroundAttachment = "fixed";
  } else {
    document.body.style.backgroundImage = "";
    document.body.style.backgroundColor = "gray";
  }
}