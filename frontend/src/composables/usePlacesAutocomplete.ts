import { onBeforeUnmount, ref, shallowRef, type Ref } from 'vue';
import { getGoogleMapsLoadHint, loadGooglePlaces } from '@/utils/googleMaps';
import {
  geocodeQueryInKosovo,
  getKosovoAutocompleteOptions,
  getKosovoPlaceAutocompleteOptions,
  placeDetailsToSelection,
  placeToSelection,
  type PlaceSelection,
} from '@/utils/places';

const PAC_CONTAINER_Z_INDEX = '120';

function stylePlaceAutocompleteElement(element: google.maps.places.PlaceAutocompleteElement) {
  element.noInputIcon = true;
  element.style.setProperty('border', 'none');
  element.style.setProperty('border-radius', '0');
  element.style.setProperty('background-color', 'transparent');
  element.style.setProperty('box-shadow', 'none');
  element.style.setProperty('width', '100%');
  element.style.setProperty('color-scheme', 'light');
}

function elevatePlacesDropdowns() {
  document.querySelectorAll<HTMLElement>('.pac-container').forEach((container) => {
    container.style.zIndex = PAC_CONTAINER_Z_INDEX;
  });
}

function startPlacesDropdownObserver() {
  elevatePlacesDropdowns();
  const observer = new MutationObserver(() => {
    elevatePlacesDropdowns();
  });
  observer.observe(document.body, { childList: true, subtree: true });
  return observer;
}

export function usePlacesAutocomplete(hostRef: Ref<HTMLElement | null>) {
  const isReady = ref(false);
  const loadError = ref<string | null>(null);
  const isSearching = ref(false);
  const autocompleteElement = shallowRef<google.maps.places.PlaceAutocompleteElement | null>(null);
  const legacyAutocomplete = shallowRef<google.maps.places.Autocomplete | null>(null);
  let selectListener: ((event: Event) => void) | null = null;
  let legacyListener: google.maps.MapsEventListener | null = null;
  let onSelectHandler: ((selection: PlaceSelection) => void) | null = null;
  let dropdownObserver: MutationObserver | null = null;

  async function initialize(onSelect: (selection: PlaceSelection) => void) {
    onSelectHandler = onSelect;
    if (!hostRef.value) {
      return;
    }

    try {
      await loadGooglePlaces();
      await mountPlaceAutocompleteElement(onSelect);
    } catch (error) {
      try {
        await mountLegacyAutocomplete(onSelect);
      } catch {
        loadError.value = getGoogleMapsLoadHint(error);
      }
    }
  }

  async function mountPlaceAutocompleteElement(onSelect: (selection: PlaceSelection) => void) {
    if (!hostRef.value) {
      return;
    }

    await google.maps.importLibrary('places');
    const element = new google.maps.places.PlaceAutocompleteElement({
      ...getKosovoPlaceAutocompleteOptions(),
    });

    stylePlaceAutocompleteElement(element);
    hostRef.value.replaceChildren(element);
    autocompleteElement.value = element;
    isReady.value = true;
    loadError.value = null;

    selectListener = async (event: Event) => {
      const placeEvent = event as google.maps.places.PlacePredictionSelectEvent;
      const prediction = placeEvent.placePrediction;
      if (!prediction) {
        return;
      }

      const selection = await placeDetailsToSelection(prediction.toPlace());
      if (selection) {
        onSelect(selection);
      }
    };

    element.addEventListener('gmp-select', selectListener);
    dropdownObserver?.disconnect();
    dropdownObserver = startPlacesDropdownObserver();
  }

  async function mountLegacyAutocomplete(onSelect: (selection: PlaceSelection) => void) {
    if (!hostRef.value) {
      return;
    }

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'location-search__legacy-input';
    input.autocomplete = 'off';
    hostRef.value.replaceChildren(input);

    await loadGooglePlaces();
    legacyAutocomplete.value = new google.maps.places.Autocomplete(
      input,
      getKosovoAutocompleteOptions(),
    );

    legacyListener = legacyAutocomplete.value.addListener('place_changed', () => {
      const place = legacyAutocomplete.value?.getPlace();
      if (!place) {
        return;
      }
      const selection = placeToSelection(place);
      if (selection) {
        onSelect(selection);
      }
    });

    isReady.value = true;
    loadError.value = null;
    dropdownObserver?.disconnect();
    dropdownObserver = startPlacesDropdownObserver();
  }

  async function searchQuery(query: string) {
    if (!onSelectHandler) {
      return false;
    }

    isSearching.value = true;
    loadError.value = null;

    try {
      const selection = await geocodeQueryInKosovo(query);
      if (selection) {
        onSelectHandler(selection);
        return true;
      }
      loadError.value = `No Kosovo match for "${query}". Try a street or city name.`;
      return false;
    } catch (error) {
      loadError.value = getGoogleMapsLoadHint(error);
      return false;
    } finally {
      isSearching.value = false;
    }
  }

  function setPlaceholder(value: string) {
    if (autocompleteElement.value) {
      autocompleteElement.value.placeholder = value;
      return;
    }

    const legacyInput = hostRef.value?.querySelector('input');
    if (legacyInput) {
      legacyInput.placeholder = value;
    }
  }

  function setDisabled(value: boolean) {
    if (autocompleteElement.value) {
      autocompleteElement.value.disabled = value;
    }

    const legacyInput = hostRef.value?.querySelector('input');
    if (legacyInput) {
      legacyInput.disabled = value;
    }
  }

  function destroy() {
    dropdownObserver?.disconnect();
    dropdownObserver = null;
    if (autocompleteElement.value && selectListener) {
      autocompleteElement.value.removeEventListener('gmp-select', selectListener);
    }
    legacyListener?.remove();
    legacyListener = null;
    selectListener = null;
    autocompleteElement.value = null;
    legacyAutocomplete.value = null;
    onSelectHandler = null;
    hostRef.value?.replaceChildren();
    isReady.value = false;
  }

  onBeforeUnmount(destroy);

  return {
    initialize,
    searchQuery,
    setPlaceholder,
    setDisabled,
    destroy,
    isReady,
    isSearching,
    loadError,
  };
}
