/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { loadJS, loadCSS } from "@web/core/assets";
import { Component, onMounted, onWillUnmount, useRef, xml } from "@odoo/owl";

export class CatastroMapWidget extends Component {
    static template = xml`
        <div class="catastro-leaflet-map-wrapper w-100">
            <div t-ref="mapContainer" style="height: 500px; width: 100%; border: 2px solid #ced4da; border-radius: 8px; z-index: 1;"></div>
            <div t-if="!props.record.data[props.name]" class="text-muted mt-2 text-center" style="font-size: 0.85em;">
                <i class="fa fa-info-circle"></i> Ingrese un polígono GeoJSON válido para renderizar automáticamente el mapa.
            </div>
        </div>
    `;
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.mapContainer = useRef("mapContainer");
        this.map = null;

        onMounted(async () => {
            // Carga asíncrona a prueba de fallos en el framework de Odoo
            await loadCSS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css");
            await loadJS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js");
            
            if (typeof L !== 'undefined') {
                this.initMap();
            } else {
                console.warn("Librería cartográfica Leaflet no disponible en este entorno.");
            }
        });

        onWillUnmount(() => {
            if (this.map) {
                this.map.remove();
            }
        });
    }

    initMap() {
        // Coordenadas céntricas referencia: Vallegrande, Santa Cruz, Bolivia
        this.map = L.map(this.mapContainer.el).setView([-18.4897, -64.1065], 15);
        
        // Capa satelital pública como base
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors | Catastro Vallegrande'
        }).addTo(this.map);

        // Detección automática de entorno: Si el puerto es 8069 (desarrollo puro WSL), apuntar a 8081. Sino usar proxy Traefik (/qgisserver).
        let wmsUrl = '/qgisserver';
        if (window.location.port === "8069") {
            wmsUrl = window.location.protocol + "//" + window.location.hostname + ":8081";
        }

        // Capa híbrida WMS dinámica alojada internamente (QGIS Server - Docker)
        L.tileLayer.wms(wmsUrl, {
            layers: 'catastro_vallegrande_base', // Capa o proyecto por detectar
            format: 'image/png',
            transparent: true,
            version: '1.3.0',
            attribution: '© GAM Vallegrande (QGIS Server en Alta Disponibilidad)'
        }).addTo(this.map);

        const capa_raw = this.props.record.data.coordenadas_json;
        if (capa_raw) {
            try {
                const geojsonData = JSON.parse(capa_raw);
                const layer = L.geoJSON(geojsonData, {
                    style: function (feature) {
                        return {color: feature.properties.color || "#ff7800", weight: 2, opacity: 0.8};
                    }
                }).addTo(this.map);
                
                // Centrar dinámicamente el visor al polígono del predio (si aplica)
                this.map.fitBounds(layer.getBounds());
            } catch (e) {
                console.error("El formato GeoJSON alojado en PostGIS/Odoo no es válido visualmente", e);
            }
        }
    }
}

// Inyección del widget en el ecosistema OWL de Odoo 17
export const catastroMapWidget = {
    component: CatastroMapWidget,
    supportedTypes: ["text", "char"],
};
registry.category("fields").add("catastro_leaflet_map", catastroMapWidget);
