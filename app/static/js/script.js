function setBackgroundImage(image_url) {
  const backgroundDiv = document.querySelector('.background');
  if (image_url) {
    console.log(image_url)
    backgroundDiv.style.backgroundImage = `url('${image_url}')`;
  } else {
    backgroundDiv.style.backgroundImage = "";
    document.body.style.backgroundColor = "gray";
  }
}

// background styler
document.addEventListener("DOMContentLoaded", () => {
  const backgroundDiv = document.querySelector('.background');
  const backgroundImageUrl = backgroundDiv.style.backgroundImage.slice(5, -2);

  const adjustBackgroundSizeAndBlur = () => {
    const aspectRatio = window.innerWidth / window.innerHeight;

    // adjust background size based on aspect ratio
    if (aspectRatio > 1) {
      backgroundDiv.style.backgroundSize = "cover";
    } else {
      backgroundDiv.style.backgroundSize = "auto 100%";
    }

    // ensure background height always covers at least the full content height
    const viewportHeight = window.innerHeight;
    const contentHeight = document.body.scrollHeight;
    backgroundDiv.style.height = `${Math.max(viewportHeight, contentHeight)}px`;

    // calculate blur based on viewport width, makes blur constant
    const blurAmount = window.innerWidth * 0.02;
    backgroundDiv.style.filter = `blur(${blurAmount}px)`;
  };

  // apply adjustments once the image has fully loaded
  const img = new Image();
  img.src = backgroundImageUrl;

  img.onload = () => {
    adjustBackgroundSizeAndBlur(); 
  };

  // add resize listener to apply adjustments dynamically
  window.addEventListener("resize", adjustBackgroundSizeAndBlur);
});
