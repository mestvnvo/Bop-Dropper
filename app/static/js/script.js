// background styler
document.addEventListener("DOMContentLoaded", () => {
  adjustBackgroundEffects();
  setupInputTruncation();
});

function setBackgroundImage(image_url) {
  const backgroundDiv = document.querySelector('.background');
  if (image_url) {
    console.log(image_url)
    backgroundDiv.style.backgroundImage = `url('${image_url}')`;
  } else {
    backgroundDiv.style.backgroundImage = "";
    document.body.style.backgroundColor = "#121212";
  }
}

function adjustBackgroundEffects() {
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
    const blurAmount = window.innerWidth * 0.015;
    backgroundDiv.style.filter = `blur(${blurAmount}px) brightness(60%)`;
  };

  // apply adjustments once the image has fully loaded
  const img = new Image();
  img.src = backgroundImageUrl;

  img.onload = () => {
    adjustBackgroundSizeAndBlur(); 
  };

  // add resize listener to apply adjustments dynamically
  window.addEventListener("resize", adjustBackgroundSizeAndBlur);
}

function setupInputTruncation() {
  const bopLinkInput = document.querySelector('input[name="bop_link"]');

  if (bopLinkInput) {
    // Add an event listener to handle input changes
    bopLinkInput.addEventListener("input", function(event) {
        const url = bopLinkInput.value;
        const truncatedUrl = url.split("?")[0];
        bopLinkInput.value = truncatedUrl;
    });
  } else {
    console.error("The input with name 'bop_link' was not found.");
  }
}
