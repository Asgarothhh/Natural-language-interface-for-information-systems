"""Тестовая коллекция документов по сфере применения варианта 7: локальная вычислительная сеть."""

from __future__ import annotations

import os
import textwrap
from typing import Sequence

import pymupdf

CORPUS: Sequence[tuple[str, str, str]] = (
    (
        "01_lan_overview.pdf",
        "Introduction to Local Area Networks",
        """
        A local area network, commonly called a LAN, connects computers, printers, servers,
        and other devices inside a limited geographic area such as an office, a laboratory,
        a classroom building, or a small campus. Unlike a wide area network, a LAN is owned
        and administered by a single organization. That organization controls cabling, switches,
        addressing policy, and access rules.

        Typical LAN services include file sharing, printer sharing, directory authentication,
        software deployment, and access to internal web applications. Workstations act as
        clients, while dedicated machines provide file, print, mail, and database services.
        A peer-to-peer LAN is possible in a very small office, but most institutional networks
        follow a client-server model because it is easier to back up data and enforce security.

        The physical reach of a LAN is short, so latency is low and bandwidth is high compared
        with the public Internet. Copper twisted-pair cable, fiber optic backbone links, and
        wireless access points are the usual media. A well designed LAN separates user access
        from server access and isolates laboratory equipment from administrative offices.

        Network administrators plan capacity, monitor utilization, and keep an inventory of
        every switch port. They also maintain documentation: floor plans, patch-panel labels,
        IP address spreadsheets, and change logs. Without that documentation, troubleshooting
        a local area network becomes slow and error-prone.

        In this collection the LAN is treated as the primary information space: documents
        describe topology, Ethernet, addressing, virtual LANs, wireless extensions, and
        security controls that protect hosts attached to the same local network.
        """,
    ),
    (
        "02_ethernet.pdf",
        "Ethernet Technology and IEEE 802.3",
        """
        Ethernet is the dominant data-link technology inside a local area network. The IEEE
        802.3 family defines frame format, media access, and physical layers for copper and
        fiber. Early shared Ethernet used carrier sense multiple access with collision detection,
        known as CSMA/CD. Hosts listened before transmitting and backed off after a collision.

        Modern Ethernet is switched and full duplex, so collisions almost never occur on
        access ports. A frame still carries a destination MAC address, a source MAC address,
        an Ethertype, a payload, and a frame check sequence. Switches learn source addresses
        and forward frames only to the required port, which raises effective bandwidth.

        Common physical standards include 10BASE-T, 100BASE-TX, 1000BASE-T, and 10GBASE-T
        on twisted pair, plus optical variants for backbone links. Auto-negotiation selects
        speed and duplex. A duplex mismatch between a switch and a workstation produces
        late collisions, CRC errors, and mysterious slowness.

        Jumbo frames can reduce interrupt load on storage networks, but every device on the
        path must agree on the maximum transmission unit. Administrators therefore treat
        jumbo frames as an optional optimization, not a default.

        Understanding Ethernet is essential for LAN design. Cabling categories, patch quality,
        and correct speed settings determine whether the network behaves like a reliable
        campus fabric or like a collision-prone shared medium from the 1990s.
        """,
    ),
    (
        "03_topologies.pdf",
        "LAN Topologies: Bus, Star, Ring, and Mesh",
        """
        Topology describes how nodes of a local area network are arranged. A bus topology
        places every station on a single coaxial cable. Terminators absorb the signal at
        both ends. The design is inexpensive, but a cable break disables the entire segment
        and troubleshooting is difficult.

        A star topology connects each workstation to a central hub or switch. This is the
        default for twisted-pair Ethernet. A failed cable affects only one host, and moves
        are simple: unplug a patch cord and plug it into another switch port. The central
        device becomes a critical point of failure, so important closets use redundant
        switches and dual power supplies.

        Ring topologies pass a token or follow a logical ring, as in legacy Token Ring and
        some metropolitan fiber rings. Mesh topologies provide multiple paths and are used
        between core switches. A hybrid campus LAN usually combines a star at the access
        layer with a partial mesh in the core.

        Choosing a topology is a reliability decision as much as a cabling decision. Star
        wiring with hierarchical switching scales from a single laboratory to a multi-floor
        building. Mesh uplinks protect against a single backbone failure. Documentation of
        the physical topology should match the logical drawing that operators keep in the
        network operations center.
        """,
    ),
    (
        "04_switching.pdf",
        "Hubs, Bridges, and LAN Switches",
        """
        Repeaters and hubs extend a collision domain: every frame is flooded to every port.
        Bridges and switches break that domain. A transparent switch maintains a MAC address
        table, learns source addresses from incoming frames, and forwards unicast traffic
        only to the destination port. Unknown unicast, broadcast, and multicast frames are
        still flooded inside the broadcast domain.

        Store-and-forward switching checks the frame check sequence before forwarding, which
        discards damaged frames. Cut-through switching starts forwarding earlier and has
        lower latency, but it can propagate errors. Most campus switches default to
        store-and-forward.

        Layer-2 loops are dangerous. Spanning Tree Protocol blocks redundant links until a
        failure occurs. Rapid spanning tree converges faster than the classic algorithm.
        Administrators should enable portfast or edge-port features only on access ports
        that connect end hosts, never on inter-switch uplinks.

        Replacing hubs with switches is the single most effective upgrade for an aging LAN.
        Each workstation receives a dedicated collision domain, full-duplex Ethernet becomes
        possible, and capture of other users' traffic requires a configured mirror port
        rather than a cheap hub.
        """,
    ),
    (
        "05_addressing.pdf",
        "IP Addressing, Subnetting, ARP, and DHCP",
        """
        Hosts on a local area network need both a hardware MAC address and a logical IP
        address. IPv4 addresses are paired with a subnet mask or CIDR prefix. The prefix
        tells a host whether the destination is on-link. If it is not, the packet is sent
        to the default gateway, usually a router or layer-3 switch on the same subnet.

        Address Resolution Protocol maps an IPv4 address to a MAC address inside the LAN
        broadcast domain. A host sends an ARP request, the owner replies, and the mapping
        is cached. Stale or poisoned ARP entries cause intermittent connectivity and are a
        common attack technique on flat networks.

        Dynamic Host Configuration Protocol assigns IP address, mask, gateway, and DNS
        servers automatically. A DHCP lease has a lifetime; clients renew it. Servers and
        printers usually receive reserved addresses so that firewall rules stay stable.
        Duplicate addresses produce a conflict and kick one of the hosts off the network.

        Careful subnetting keeps broadcast traffic local and prepares the LAN for VLAN
        segmentation. A laboratory subnet, a staff subnet, and a guest subnet should not
        share one giant prefix. Documentation of DHCP scopes and static reservations is
        part of daily LAN operations.
        """,
    ),
    (
        "06_vlan.pdf",
        "Virtual LANs and Traffic Segmentation",
        """
        A virtual LAN, or VLAN, groups switch ports into separate broadcast domains even
        when they share the same physical switch. IEEE 802.1Q inserts a tag into the
        Ethernet frame on trunk links. Access ports belong to a single VLAN and send
        untagged frames to workstations.

        Segmentation by VLAN limits broadcast traffic and supports security policy. Finance
        workstations, laboratory instruments, IP telephones, and guest laptops can share
        one switch stack yet remain isolated. Inter-VLAN communication requires a router
        or a layer-3 switch. Access control lists on that device decide which subnets may
        talk to each other.

        Poor VLAN design recreates a flat network. Placing every port in VLAN 1, using
        the native VLAN for user data, or allowing user ports to negotiate trunking opens
        the door to VLAN hopping. Best practice is a dedicated unused native VLAN, explicit
        trunk allow-lists, and unused ports parked in a black-hole VLAN.

        Voice VLANs and data VLANs on the same access port are common. The telephone uses
        the tagged voice VLAN, while the PC behind the telephone uses the untagged data
        VLAN. Quality of service markings then protect latency-sensitive voice packets
        across the campus LAN.
        """,
    ),
    (
        "07_wireless.pdf",
        "Wireless LAN, Wi-Fi Standards, and Access Points",
        """
        A wireless LAN extends the wired campus with radio access points. IEEE 802.11
        families, marketed as Wi-Fi, define channels, modulation, and frame formats.
        Users associate with a service set identifier advertised by one or more access
        points. Roaming occurs when a client moves and reassociates with a stronger radio.

        Coverage planning matters. Overlapping channels on 2.4 GHz cause interference.
        The 5 GHz and 6 GHz bands offer more non-overlapping channels and higher throughput,
        especially with MIMO spatial streams. Concrete walls, microwave ovens, and poorly
        placed antennas create dead zones that no software setting can repair.

        Wireless is still a LAN: clients receive DHCP leases, use ARP, and reach the same
        default gateway as wired neighbors if they share a VLAN. Many organizations place
        wireless users in a dedicated subnet and filter that subnet more strictly. Guest
        Wi-Fi should never be bridged directly onto the internal staff VLAN.

        Security for wireless LAN includes WPA2 or WPA3, 802.1X enterprise authentication,
        and rogue access point detection. An open access point in a conference room is a
        convenient service and a convenient attack surface. Controllers or cloud-managed
        access points help keep firmware current and SSIDs consistent across buildings.
        """,
    ),
    (
        "08_security.pdf",
        "LAN Security: Firewalls, Access Control, and Hardening",
        """
        Hosts that share a local area network can often reach one another without crossing
        an Internet firewall. Lateral movement is therefore a first-class risk. Defenses
        start with physical control of switch closets and continue with port security,
        802.1X authentication, and network access control that checks a laptop before
        it receives a productive VLAN.

        Access control lists on layer-3 boundaries restrict which subnets may connect
        to management interfaces, file servers, and building automation. A host-based
        firewall on each workstation adds defense in depth. Unused services should be
        disabled so that a compromised printer cannot scan the entire campus.

        Switch hardening includes a secure management VLAN, encrypted administration
        protocols, disabled unused ports, and storm control against broadcast floods.
        DHCP snooping and dynamic ARP inspection reduce spoofing on access switches.
        Logging should be sent to a collector so that port flaps and authentication
        failures are visible.

        Encryption protects data that leaves the building, but inside the LAN many
        protocols remain cleartext unless administrators insist on TLS and SSH. Regular
        reviews of firewall rules, VLAN maps, and user accounts keep the local network
        from slowly returning to a single trusted soup of devices.
        """,
    ),
)


def _normalize_body(title: str, body: str) -> str:
    paragraphs = [" ".join(line.split()) for line in body.strip().split("\n\n")]
    return title + "\n\n" + "\n\n".join(paragraphs)


def write_pdf(path: str, title: str, body: str) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    y = 56
    page.insert_text((50, y), title, fontsize=16, fontname="helv")
    y += 28
    for paragraph in _normalize_body(title, body).split("\n\n")[1:]:
        for line in textwrap.wrap(paragraph, width=88) or [""]:
            if y > 800:
                page = doc.new_page(width=595, height=842)
                y = 56
            page.insert_text((50, y), line, fontsize=11, fontname="helv")
            y += 15
        y += 8
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc.save(path)
    doc.close()


def ensure_corpus(documents_dir: str) -> list[str]:
    """Создаёт PDF-коллекцию, если файлов ещё нет, и возвращает пути."""
    os.makedirs(documents_dir, exist_ok=True)
    paths = []
    for filename, title, body in CORPUS:
        path = os.path.join(documents_dir, filename)
        if not os.path.exists(path):
            write_pdf(path, title, body)
        paths.append(path)
    return paths
